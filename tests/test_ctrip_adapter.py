import json
import unittest
from pathlib import Path

from crawler.adapters.ctrip import CtripCampusAdapter


class CtripAdapterTests(unittest.TestCase):
    def test_normalizes_public_job_fixture(self):
        raw = json.loads((Path(__file__).parent / "fixtures" / "ctrip_job.json").read_text(encoding="utf-8"))
        job = CtripCampusAdapter().normalize({
            "id": "ctrip-campus-api",
            "company": "携程集团",
            "url": "https://careers.ctrip.com/#/campus/jobList?kind=1",
            "campus_only": True,
        }, raw)
        self.assertIsNotNone(job)
        self.assertEqual(job["source_job_id"], "MJ036832")
        self.assertEqual(job["city"], "伦敦")
        self.assertEqual(job["job_nature"], "全职")
        self.assertEqual(job["graduate_year"], "2027")
        self.assertIn("/campus/job-detail/MJ036832", job["apply_url"])
        self.assertIn("产品全生命周期", job["description"])
        self.assertIn("人工智能", job["requirements"])


if __name__ == "__main__":
    unittest.main()
