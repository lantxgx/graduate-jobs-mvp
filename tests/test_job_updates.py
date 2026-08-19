import tempfile
import unittest
from pathlib import Path

from app import db


class JobUpdatesTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_db = db.DB_PATH
        db.DB_PATH = Path(self.temp_dir.name) / "jobs.db"
        db.init_db()

    def tearDown(self):
        db.DB_PATH = self.old_db
        self.temp_dir.cleanup()

    def test_new_job_is_visible_in_change_feed(self):
        db.upsert_job({
            "source_id": "fixture",
            "source_job_id": "job-1",
            "company": "Acme",
            "title": "软件研发工程师",
            "city": "北京",
            "job_nature": "全职",
            "category": "软件研发",
            "degree": "本科及以上",
            "description": "负责软件研发工作",
            "requirements": "本科及以上",
            "apply_url": "https://acme.example/jobs/1",
            "source_url": "https://acme.example/jobs",
            "content_hash": "hash-1",
        })
        rows = db.query_job_updates(limit=10)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["source_job_id"], "job-1")
        self.assertEqual(rows[0]["update_time"], rows[0]["first_seen_at"])

    def test_since_filter_excludes_older_rows(self):
        db.upsert_job({
            "source_id": "fixture",
            "source_job_id": "job-1",
            "company": "Acme",
            "title": "软件研发工程师",
            "city": "北京",
            "job_nature": "全职",
            "category": "软件研发",
            "degree": "本科及以上",
            "description": "负责软件研发工作",
            "requirements": "本科及以上",
            "apply_url": "https://acme.example/jobs/1",
            "source_url": "https://acme.example/jobs",
            "content_hash": "hash-1",
        })
        self.assertEqual(db.query_job_updates("2999-01-01T00:00:00", 10), [])


if __name__ == "__main__":
    unittest.main()
