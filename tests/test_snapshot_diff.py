import tempfile
import unittest
from pathlib import Path

from app import db


class SnapshotDiffTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.previous_db_path = db.DB_PATH
        db.DB_PATH = Path(self.temp_dir.name) / "jobs.db"
        db.init_db()
        db.upsert_job({
            "source_id": "snapshot-source",
            "source_job_id": "job-1",
            "company": "Example",
            "title": "Backend Engineer",
            "city": "Beijing",
            "job_nature": "全职",
            "category": "软件研发",
            "degree": "本科及以上",
            "description": "Build services.",
            "source_url": "https://example.com/jobs",
            "apply_url": "https://example.com/jobs/job-1",
            "content_hash": "job-1-v1",
            "raw": {},
        })

    def tearDown(self):
        db.DB_PATH = self.previous_db_path
        self.temp_dir.cleanup()

    def _state(self):
        with db.connect() as conn:
            return conn.execute(
                "SELECT status, missing_snapshot_count FROM jobs WHERE source_id='snapshot-source'"
            ).fetchone()

    def test_three_complete_missing_snapshots_before_deactivation(self):
        self.assertEqual(db.deactivate_missing_jobs("snapshot-source", ["other"]), 0)
        self.assertEqual(tuple(self._state()), ("active", 1))
        self.assertEqual(db.deactivate_missing_jobs("snapshot-source", ["other"]), 0)
        self.assertEqual(tuple(self._state()), ("active", 2))
        self.assertEqual(db.deactivate_missing_jobs("snapshot-source", ["other"]), 1)
        self.assertEqual(tuple(self._state()), ("inactive", 3))

    def test_reappearing_job_is_reactivated_and_counter_reset(self):
        for _ in range(2):
            db.deactivate_missing_jobs("snapshot-source", ["other"])
        db.upsert_job({
            "source_id": "snapshot-source",
            "source_job_id": "job-1",
            "company": "Example",
            "title": "Backend Engineer",
            "city": "Beijing",
            "job_nature": "全职",
            "category": "软件研发",
            "degree": "本科及以上",
            "description": "Changed details.",
            "source_url": "https://example.com/jobs",
            "apply_url": "https://example.com/jobs/job-1",
            "content_hash": "job-1-v2",
            "raw": {},
        })
        self.assertEqual(tuple(self._state()), ("active", 0))


if __name__ == "__main__":
    unittest.main()
