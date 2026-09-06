import json
import unittest
from pathlib import Path

from crawler.adapters.wind import WindCampusAdapter


class WindAdapterTests(unittest.TestCase):
    def test_normalizes_public_position_fixture(self):
        fixture = Path(__file__).parent / "fixtures" / "wind_position.json"
        raw = json.loads(fixture.read_text(encoding="utf-8"))
        source = {
            "id": "source-de915a7057089add",
            "company": "万得资讯",
            "url": "https://www.wind.com.cn/portal/zh/JoinUs/recruit.html",
            "campus_only": True,
        }
        job = WindCampusAdapter().normalize(source, raw)
        self.assertIsNotNone(job)
        self.assertEqual(job["source_job_id"], "1404")
        self.assertEqual(job["job_nature"], "实习")
        self.assertEqual(job["city"], "上海")
        self.assertEqual(job["degree"], "本科及以上")
        self.assertIn("channelPositionId=1404", job["apply_url"])


if __name__ == "__main__":
    unittest.main()
