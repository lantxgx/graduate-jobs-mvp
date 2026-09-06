import json
import unittest
from pathlib import Path

from crawler.adapters.gbits import GbitsCampusAdapter


class GbitsAdapterTests(unittest.TestCase):
    def test_normalizes_public_position_fixture(self):
        raw = json.loads((Path(__file__).parent / "fixtures" / "gbits_position.json").read_text(encoding="utf-8"))
        source = {
            "id": "gbits-campus",
            "company": "吉比特",
            "url": "https://hr.g-bits.com/web/index.html#/home-web/home-index",
            "campus_only": True,
        }
        job = GbitsCampusAdapter().normalize(source, raw)
        self.assertIsNotNone(job)
        self.assertEqual(job["job_nature"], "全职")
        self.assertEqual(job["degree"], "本科及以上")
        self.assertEqual(job["city"], "Shenzhen")
        self.assertEqual(job["source_job_id"], raw["id"])


if __name__ == "__main__":
    unittest.main()
