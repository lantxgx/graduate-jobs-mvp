import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app import db
from app.main import app


class JobPaginationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.previous_db_path = db.DB_PATH
        db.DB_PATH = Path(self.temp_dir.name) / "jobs.db"
        self.client = TestClient(app)
        db.init_db()
        for index in range(5):
            db.upsert_job({
                "source_id": "pagination",
                "job_nature": "全职",
                "company": "Example",
                "title": f"Position {index}",
                "city": "Beijing",
                "source_url": f"https://example.com/jobs/{index}",
                "apply_url": f"https://example.com/jobs/{index}",
                "content_hash": f"pagination-{index}",
                "raw": {},
            })

    def tearDown(self):
        self.client.close()
        db.DB_PATH = self.previous_db_path
        self.temp_dir.cleanup()

    def test_legacy_jobs_response_remains_a_list(self):
        response = self.client.get("/api/jobs?limit=2")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_offset_response_contains_metadata_and_no_duplicates(self):
        first = self.client.get("/api/jobs?limit=2&offset=0").json()
        second = self.client.get("/api/jobs?limit=2&offset=2").json()
        self.assertEqual(first["total"], 5)
        self.assertEqual(len(first["items"]), 2)
        self.assertEqual(len(second["items"]), 2)
        self.assertTrue(set(item["id"] for item in first["items"]).isdisjoint(item["id"] for item in second["items"]))

    def test_filter_total_matches_filtered_items(self):
        result = self.client.get("/api/jobs?company=Example&city=Beijing&limit=3&offset=3").json()
        self.assertEqual(result["total"], 5)
        self.assertEqual(len(result["items"]), 2)


if __name__ == "__main__":
    unittest.main()
