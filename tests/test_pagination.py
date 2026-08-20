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

    def test_multi_city_jobs_use_array_and_atomic_facets(self):
        db.upsert_job({
            "source_id": "pagination",
            "source_job_id": "multi-city",
            "job_nature": "全职",
            "company": "Example",
            "title": "Multi City Position",
            "city": "北京市-北京市 / 广东省-深圳市 / 上海市-上海市",
            "requirements": "计算机、软件工程、人工智能等相关专业",
            "source_url": "https://example.com/jobs/multi-city",
            "apply_url": "https://example.com/jobs/multi-city",
            "content_hash": "pagination-multi-city",
            "raw": {},
        })
        facets = self.client.get("/api/facets").json()
        self.assertIn("北京", facets["cities"])
        self.assertIn("深圳", facets["cities"])
        self.assertIn("上海", facets["cities"])
        self.assertNotIn("北京市-北京市 / 广东省-深圳市 / 上海市-上海市", facets["cities"])
        self.assertIn("计算机类", facets["majors"])
        self.assertIn({"country": "中国", "province": "广东", "city": "深圳"}, facets["locations"])
        result = self.client.get("/api/jobs?city=深圳&limit=10&offset=0").json()
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["items"][0]["work_locations"], ["北京", "深圳", "上海"])
        self.assertEqual(result["items"][0]["major_requirements"], ["计算机类", "软件工程", "人工智能"])
        hierarchical = self.client.get("/api/jobs?country=中国&province=广东&city=深圳&major=人工智能&limit=10&offset=0").json()
        self.assertEqual(hierarchical["total"], 1)


if __name__ == "__main__":
    unittest.main()
