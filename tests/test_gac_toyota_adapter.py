import json
import unittest
from pathlib import Path

from crawler.adapters.gac_toyota import GacToyotaCampusAdapter


class GacToyotaAdapterTests(unittest.TestCase):
    def test_normalizes_public_detail_fixture(self):
        raw = json.loads((Path(__file__).parent / "fixtures" / "gac_toyota_job.json").read_text(encoding="utf-8"))
        job = GacToyotaCampusAdapter().normalize({
            "id": "gac-toyota-campus",
            "company": "广汽丰田",
            "url": "https://gac-toyota.zhiye.com/campus/jobs",
        }, raw)
        self.assertIsNotNone(job)
        self.assertEqual(job["city"], "广州")
        self.assertEqual(job["category"], "硬件研发")
        self.assertEqual(job["degree"], "本科及以上")
        self.assertEqual(job["source_job_id"], "621117741")


if __name__ == "__main__":
    unittest.main()
