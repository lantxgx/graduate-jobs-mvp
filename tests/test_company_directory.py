import tempfile
import unittest
from pathlib import Path

from app import db
from crawler.company_directory import import_directory


WORKBOOK = Path("outputs/019fe088-133d-7612-8425-8d152dbf8426/official_campus_career_sites.xlsx")


class CompanyDirectoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.previous_db_path = db.DB_PATH
        db.DB_PATH = Path(self.temp_dir.name) / "jobs.db"

    def tearDown(self):
        db.DB_PATH = self.previous_db_path
        self.temp_dir.cleanup()

    def test_dry_run_reads_directory_without_writing(self):
        result = import_directory(WORKBOOK, dry_run=True)
        self.assertEqual(result["records"], 60)
        self.assertEqual(result["excluded"], 3)
        self.assertFalse(db.DB_PATH.exists())

    def test_import_is_idempotent_and_does_not_create_jobs(self):
        first = import_directory(WORKBOOK)
        second = import_directory(WORKBOOK)
        self.assertEqual(first["companies_created"], 52)
        self.assertEqual(first["sources_created"], 60)
        self.assertEqual(second["companies_created"], 0)
        self.assertEqual(second["sources_created"], 0)
        self.assertEqual(second["sources_updated"], 60)
        with db.connect() as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0], 52)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM career_sources").fetchone()[0], 60)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0], 0)

    def test_quality_and_priority_are_conservative(self):
        import_directory(WORKBOOK)
        with db.connect() as conn:
            quality = {
                row[0]: row[1]
                for row in conn.execute(
                    "SELECT quality_level, COUNT(*) FROM career_sources GROUP BY quality_level"
                ).fetchall()
            }
            priorities = {
                row[0]: row[1]
                for row in conn.execute(
                    "SELECT integration_priority, COUNT(*) FROM career_sources GROUP BY integration_priority"
                ).fetchall()
            }
        self.assertEqual(quality, {"blocked": 10, "high": 3, "low": 2, "medium": 45})
        self.assertEqual(priorities, {0: 3, 1: 4, 2: 41, 4: 12})

    def test_snapshot_protection_blocks_empty_and_sudden_drop(self):
        db.init_db()
        db.record_source_snapshot("fixture", "success", 100, 100, 100)
        self.assertEqual(db.snapshot_protection("fixture", 0)[:2], (True, "empty_snapshot"))
        self.assertEqual(
            db.snapshot_protection("fixture", 40)[:2], (True, "sudden_drop_over_50_percent")
        )
        self.assertEqual(db.snapshot_protection("fixture", 60)[:2], (False, None))

    def test_crawl_cooldown_is_enforced_from_last_run(self):
        db.init_db()
        with db.connect() as conn:
            conn.execute("INSERT INTO crawl_runs(source_id, status) VALUES (?, 'success')", ("fixture",))
        self.assertGreater(db.crawl_cooldown_remaining("fixture", 3600), 0)

    def test_ingestion_queue_excludes_blocked_and_excluded_sources(self):
        import_directory(WORKBOOK)
        queue = db.query_ingestion_queue(500)
        self.assertTrue(queue)
        self.assertTrue(all(item["access_status"] == "reachable" for item in queue))
        self.assertTrue(all(item["official_status"] in {"confirmed", "candidate"} for item in queue))
        self.assertTrue(all("adapter" in item for item in queue))
        self.assertTrue(all("paused_reason" in item for item in queue))


if __name__ == "__main__":
    unittest.main()
