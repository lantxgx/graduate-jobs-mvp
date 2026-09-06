import json
import unittest
from pathlib import Path

from crawler.adapters.bilibili import BilibiliCampusAdapter


class BilibiliAdapterTests(unittest.TestCase):
    SOURCE = {
        "id": "bilibili-campus-roster",
        "company": "哔哩哔哩",
        "url": "https://jobs.bilibili.com/campus/positions?type=1",
        "campus_only": True,
    }

    def test_normalizes_public_detail_fixture(self):
        raw = json.loads((Path(__file__).parent / "fixtures" / "bilibili_position.json").read_text(encoding="utf-8"))
        job = BilibiliCampusAdapter().normalize(self.SOURCE, raw)
        self.assertIsNotNone(job)
        self.assertEqual(job["company"], "哔哩哔哩")
        self.assertEqual(job["city"], "上海")
        self.assertEqual(job["job_nature"], "全职")
        self.assertEqual(job["degree"], "本科及以上")
        self.assertEqual(job["source_job_id"], "30368")
        self.assertIn("/campus/positions/30368?type=3", job["apply_url"])
        self.assertIn("版本规划", job["description"])
        self.assertIn("2027届", job["requirements"])


if __name__ == "__main__":
    unittest.main()
