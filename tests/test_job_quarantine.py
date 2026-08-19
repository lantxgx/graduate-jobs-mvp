import tempfile
import unittest
from pathlib import Path

from app import db


class JobQuarantineTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.previous_db_path = db.DB_PATH
        db.DB_PATH = Path(self.temp_dir.name) / "jobs.db"

    def tearDown(self):
        db.DB_PATH = self.previous_db_path
        self.temp_dir.cleanup()

    def test_rejected_observation_is_preserved_and_deduplicated(self):
        db.record_job_quarantine("fixture", "42", "Doctor Program", "normalization_rejected", {"id": 42})
        db.record_job_quarantine("fixture", "42", "Doctor Program", "normalization_rejected", {"id": 42, "seen": 2})
        rows = db.query_job_quarantine("fixture")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["source_job_id"], "42")
        self.assertEqual(rows[0]["reason"], "normalization_rejected")
        self.assertIn('"seen": 2', rows[0]["raw_json"])
        self.assertIn("company_name", rows[0])

    def test_source_filter_is_applied(self):
        db.record_job_quarantine("one", "1", "A", "quality_gate_rejected", {})
        db.record_job_quarantine("two", "2", "B", "quality_gate_rejected", {})
        self.assertEqual(len(db.query_job_quarantine("one")), 1)
        self.assertEqual(len(db.query_job_quarantine("missing")), 0)

    def test_quality_summary_reports_rejected_observations(self):
        db.record_job_quarantine("fixture", "3", "Other", "quality_gate_rejected", {})
        self.assertEqual(db.job_quality_summary()["rejected_observations"], 1)


if __name__ == "__main__":
    unittest.main()
