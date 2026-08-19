import json
import tempfile
import unittest
from pathlib import Path

from app import db
from crawler.source_registry import (
    promote_verified_sources,
    reconcile_company_registry,
    sync_config_sources,
)


class SourceRegistryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_db = db.DB_PATH
        db.DB_PATH = Path(self.temp_dir.name) / "jobs.db"

    def tearDown(self):
        db.DB_PATH = self.old_db
        self.temp_dir.cleanup()

    def test_sync_registers_sources_but_never_enables_scheduler(self):
        config = Path(self.temp_dir.name) / "sources.json"
        config.write_text(json.dumps([{
            "id": "acme-campus",
            "company": "Acme",
            "name": "Acme 校招",
            "url": "https://acme.jobs.feishu.cn/campus",
            "mode": "feishu_jobs_browser",
        }]), encoding="utf-8")
        result = sync_config_sources(config)
        self.assertEqual(result["created"], 1)
        with db.connect() as conn:
            row = conn.execute(
                "SELECT official_status, access_status, integration_status, adapter, ats_type FROM career_sources"
            ).fetchone()
        self.assertEqual(tuple(row), ("candidate", "unknown", "analyzing", "feishu_jobs_browser", "feishu"))
        # Unknown access is intentionally not placed in the executable queue.
        self.assertEqual(db.query_ingestion_queue(10), [])
        self.assertEqual(sync_config_sources(config)["updated"], 1)
        with db.connect() as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0], 0)

    def test_sync_reuses_same_url_registered_by_directory(self):
        config = Path(self.temp_dir.name) / "sources.json"
        config.write_text(json.dumps([{
            "id": "config-key",
            "company": "Acme",
            "name": "Acme 校招",
            "url": "https://acme.example/jobs",
            "mode": "browser_json",
        }]), encoding="utf-8")
        db.init_db()
        with db.connect() as conn:
            conn.execute(
                """INSERT INTO companies(canonical_name, brand_name) VALUES ('Acme', 'Acme')"""
            )
            company_id = conn.execute("SELECT id FROM companies WHERE canonical_name='Acme'").fetchone()[0]
            conn.execute(
                """INSERT INTO career_sources(
                   source_key, company_id, source_name, url, recruitment_scope,
                   ats_type, official_status, access_status, integration_status
                ) VALUES ('generated-key', ?, 'Acme', 'https://acme.example/jobs',
                          'campus', 'custom', 'candidate', 'unknown', 'analyzing')""",
                (company_id,),
            )
        sync_config_sources(config)
        with db.connect() as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM career_sources").fetchone()[0], 1)
            self.assertEqual(conn.execute("SELECT source_key FROM career_sources").fetchone()[0], "config-key")

    def test_verified_reconciliation_promotes_only_allowlisted_sources_with_active_jobs(self):
        db.init_db()
        with db.connect() as conn:
            company_id = conn.execute(
                "INSERT INTO companies(canonical_name, brand_name) VALUES ('Xiaomi', 'Xiaomi')"
            ).lastrowid
            conn.execute(
                """INSERT INTO career_sources(
                   source_key, company_id, source_name, url, adapter,
                   official_status, access_status, integration_status,
                   quality_level, integration_priority
                ) VALUES ('xiaomi-campus', ?, 'Xiaomi', 'https://example/jobs',
                          'xiaomi_jobs_browser', 'candidate', 'unknown', 'analyzing', 'low', 3)""",
                (company_id,),
            )
            conn.execute(
                """INSERT INTO jobs(
                   source_id, source_job_id, company, title, city, job_nature,
                   category, degree, apply_url, source_url, content_hash
                ) VALUES ('xiaomi-campus', '1', 'Xiaomi', 'Engineer', 'Shanghai',
                          '全职', '软件研发', '本科及以上', 'https://example/jobs/1',
                          'https://example/jobs', 'hash-1')"""
            )
        result = promote_verified_sources()
        self.assertIn("xiaomi-campus", result["promoted"])
        with db.connect() as conn:
            row = conn.execute(
                "SELECT official_status, access_status, integration_status, quality_level, integration_priority FROM career_sources WHERE source_key='xiaomi-campus'"
            ).fetchone()
        self.assertEqual(tuple(row), ("confirmed", "reachable", "integrated", "high", 0))

    def test_xiaomi_future_refresh_is_bounded_and_not_a_complete_snapshot(self):
        config = json.loads(Path("config/sources.json").read_text(encoding="utf-8"))
        xiaomi = next(item for item in config if item["id"] == "xiaomi-campus")
        self.assertEqual(xiaomi["max_pages"], 2)
        self.assertFalse(xiaomi["snapshot_complete"])

    def test_sync_resolves_known_company_alias_to_canonical_company(self):
        config = Path(self.temp_dir.name) / "sources.json"
        config.write_text(json.dumps([{
            "id": "xiaomi-campus",
            "company": "小米集团",
            "name": "Xiaomi campus",
            "url": "https://xiaomi.example/jobs",
            "mode": "xiaomi_jobs_browser",
        }], ensure_ascii=False), encoding="utf-8")
        db.init_db()
        with db.connect() as conn:
            company_id = conn.execute(
                "INSERT INTO companies(canonical_name, brand_name) VALUES ('小米', '小米')"
            ).lastrowid
        sync_config_sources(config)
        with db.connect() as conn:
            row = conn.execute(
                "SELECT company_id FROM career_sources WHERE source_key='xiaomi-campus'"
            ).fetchone()
        self.assertEqual(row[0], company_id)

    def test_company_reconciliation_merges_explicit_alias_without_deleting_rows(self):
        db.init_db()
        with db.connect() as conn:
            target_id = conn.execute(
                "INSERT INTO companies(canonical_name, brand_name) VALUES ('OPPO', 'OPPO')"
            ).lastrowid
            duplicate_id = conn.execute(
                "INSERT INTO companies(canonical_name, brand_name) VALUES ('oppo', 'oppo')"
            ).lastrowid
            conn.execute(
                """INSERT INTO career_sources(
                   source_key, company_id, source_name, url, adapter,
                   official_status, access_status, integration_status
                ) VALUES ('oppo-alias', ?, 'OPPO alias', 'https://oppo.example',
                          'oppo', 'candidate', 'unknown', 'analyzing')""",
                (duplicate_id,),
            )
        result = reconcile_company_registry()
        self.assertEqual(result["merged"], [{"alias": "oppo", "canonical": "OPPO"}])
        with db.connect() as conn:
            source = conn.execute(
                "SELECT company_id FROM career_sources WHERE source_key='oppo-alias'"
            ).fetchone()
            duplicate = conn.execute(
                "SELECT status FROM companies WHERE id=?", (duplicate_id,)
            ).fetchone()
        self.assertEqual(source[0], target_id)
        self.assertEqual(duplicate[0], "merged")


if __name__ == "__main__":
    unittest.main()
