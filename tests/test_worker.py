import tempfile
import unittest
import asyncio
from unittest.mock import AsyncMock, patch
from pathlib import Path

from app import db


class CrawlLockTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.previous_db_path = db.DB_PATH
        db.DB_PATH = Path(self.temp_dir.name) / "jobs.db"
        db.init_db()

    def tearDown(self):
        db.DB_PATH = self.previous_db_path
        self.temp_dir.cleanup()

    def test_same_source_is_single_owner_and_releasable(self):
        self.assertTrue(db.acquire_crawl_lock("source-a", "owner-1"))
        self.assertFalse(db.acquire_crawl_lock("source-a", "owner-2"))
        self.assertTrue(db.release_crawl_lock("source-a", "owner-1"))
        self.assertTrue(db.acquire_crawl_lock("source-a", "owner-2"))

    def test_manual_worker_run_records_next_schedule(self):
        with db.connect() as conn:
            company_id = conn.execute(
                "INSERT INTO companies(canonical_name, brand_name) VALUES ('Acme', 'Acme')"
            ).lastrowid
            conn.execute(
                """INSERT INTO career_sources(
                   source_key, company_id, source_name, url, adapter,
                   official_status, access_status, integration_status
                ) VALUES ('acme-campus', ?, 'Acme campus', 'https://acme.example/jobs',
                          'legacy', 'confirmed', 'reachable', 'integrated')""",
                (company_id,),
            )

        from crawler.worker import run_one
        with patch("crawler.worker.load_sources", return_value=[{
            "id": "acme-campus",
            "company": "Acme",
            "url": "https://acme.example/jobs",
            "adapter": "legacy",
        }]), patch(
            "crawler.worker.crawl_source",
            new=AsyncMock(return_value={"source_id": "acme-campus", "jobs_found": 1}),
        ):
            result = asyncio.run(run_one("acme-campus", update_schedule=True))

        self.assertTrue(result["accepted"])
        with db.connect() as conn:
            row = conn.execute(
                "SELECT last_success_at, next_run_at, consecutive_failures FROM career_sources WHERE source_key='acme-campus'"
            ).fetchone()
        self.assertIsNotNone(row[0])
        self.assertIsNotNone(row[1])
        self.assertEqual(row[2], 0)


if __name__ == "__main__":
    unittest.main()
