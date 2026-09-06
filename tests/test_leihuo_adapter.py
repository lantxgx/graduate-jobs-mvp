import json
import unittest
from pathlib import Path

from crawler.adapters.leihuo import LeihuoCampusAdapter


class LeihuoAdapterTest(unittest.TestCase):
    def setUp(self):
        self.source = {
            "id": "leihuo-campus",
            "company": "网易游戏雷火",
            "url": "https://leihuo.163.com/campus",
            "mode": "leihuo",
            "campus_only": True,
        }
        fixture = Path(__file__).parent / "fixtures" / "leihuo_position.json"
        self.raw = json.loads(fixture.read_text(encoding="utf-8"))

    def test_normalize_public_detail(self):
        job = LeihuoCampusAdapter().normalize(self.source, self.raw)
        self.assertIsNotNone(job)
        self.assertEqual(job["company"], "网易游戏雷火")
        self.assertEqual(job["source_job_id"], "3738")
        self.assertEqual(job["job_nature"], "全职")
        self.assertEqual(job["city"], "杭州")
        self.assertEqual(job["graduate_year"], "2027")
        self.assertEqual(job["degree"], "未注明")
        self.assertTrue(job["apply_url"].startswith("https://campus.163.com/"))


if __name__ == "__main__":
    unittest.main()
