import json
import unittest
from pathlib import Path

from crawler.adapters.lixiang import LixiangCampusAdapter


SOURCE = {
    "id": "lixiang-campus-api",
    "company": "理想汽车",
    "url": "https://www.lixiang.com/employ/campus.html?fromJob=1",
    "campus_only": True,
}


class LixiangAdapterTests(unittest.TestCase):
    def test_normalizes_public_detail_fixture(self):
        raw = json.loads(
            (Path(__file__).parent / "fixtures" / "lixiang_job.json").read_text(encoding="utf-8")
        )
        raw.update({
            "source_job_id": str(raw["id"]),
            "city": raw["location_title"],
            "job_nature": raw["job_mode_name"],
            "category": raw["second_job_function_title"],
            "requirements": raw["requirements"],
        })
        job = LixiangCampusAdapter().normalize(SOURCE, raw)
        self.assertIsNotNone(job)
        self.assertEqual(job["company"], "理想汽车")
        self.assertEqual(job["city"], "上海")
        self.assertEqual(job["job_nature"], "实习")
        self.assertIn("PyTorch", job["requirements"])
        self.assertIn("/employ/detail/18946.html", job["apply_url"])


if __name__ == "__main__":
    unittest.main()
