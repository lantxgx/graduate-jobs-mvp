import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from app import db
from crawler.scheduler import record_scheduler_result, select_due_sources


class SchedulerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.previous_db_path = db.DB_PATH
        db.DB_PATH = Path(self.temp_dir.name) / "jobs.db"
        db.init_db()
        with db.connect() as conn:
            conn.execute(
                "INSERT INTO companies(canonical_name, brand_name, official_website) VALUES (?, ?, ?)",
                ("Acme", "Acme", "https://acme.example"),
            )
            company_id = conn.execute("SELECT id FROM companies WHERE canonical_name='Acme'").fetchone()[0]
            conn.execute(
                """INSERT INTO career_sources(
                   source_key, company_id, source_name, url, official_status,
                   access_status, integration_status, next_run_at
                ) VALUES (?, ?, ?, ?, 'confirmed', 'reachable', 'integrated', ?)""",
                ("acme", company_id, "Acme campus", "https://acme.example/campus", "2020-01-01 00:00:00"),
            )
            conn.execute(
                """INSERT INTO career_sources(
                   source_key, company_id, source_name, url, official_status,
                   access_status, integration_status, paused_reason
                ) VALUES (?, ?, ?, ?, 'confirmed', 'reachable', 'integrated', 'captcha')""",
                ("paused", company_id, "Paused", "https://acme.example/paused"),
            )

    def tearDown(self):
        db.DB_PATH = self.previous_db_path
        self.temp_dir.cleanup()

    def test_only_due_unpaused_integrated_sources_are_selected(self):
        rows = select_due_sources(now=datetime(2026, 1, 1, tzinfo=timezone.utc))
        self.assertEqual([row["source_key"] for row in rows], ["acme"])

    def test_protected_stop_reasons_pause_source_without_scheduling_retry(self):
        source_id = 1
        record_scheduler_result(source_id, False, "verification_page_detected")
        with db.connect() as conn:
            row = conn.execute(
                "SELECT paused_reason, next_run_at, consecutive_failures FROM career_sources WHERE id=?",
                (source_id,),
            ).fetchone()
        self.assertEqual(row[0], "verification_page_detected")
        self.assertIsNone(row[1])
        self.assertEqual(row[2], 1)

    def test_normal_failure_uses_backoff(self):
        source_id = 1
        record_scheduler_result(source_id, False, "bounded_probe_timeout")
        with db.connect() as conn:
            row = conn.execute(
                "SELECT paused_reason, next_run_at, consecutive_failures FROM career_sources WHERE id=?",
                (source_id,),
            ).fetchone()
        self.assertIsNone(row[0])
        self.assertIsNotNone(row[1])
        self.assertEqual(row[2], 1)


if __name__ == "__main__":
    unittest.main()
