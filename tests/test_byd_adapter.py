import json
import unittest
from pathlib import Path

from crawler.adapters.byd import BydCampusAdapter


class BydAdapterTests(unittest.TestCase):
    def test_normalizes_public_detail_fixture(self):
        fixture = Path(__file__).parent / "fixtures" / "byd_position.json"
        raw = json.loads(fixture.read_text(encoding="utf-8"))
        source = {
            "id": "byd-campus",
            "company": "比亚迪",
            "url": "https://job.byd.com/portal/pc/#/school/schoolPositionList",
            "campus_only": True,
        }
        job = BydCampusAdapter().normalize(source, raw)
        self.assertIsNotNone(job)
        self.assertEqual(job["source_job_id"], "2089623328531697666:2089623336307937282")
        self.assertEqual(job["job_nature"], "全职")
        self.assertEqual(job["degree"], "本科及以上")
        self.assertEqual(job["city"], "芜湖市 / 汕头市 / 深圳市")
        self.assertIn("schoolPortal/queryPosition", job["apply_url"])


if __name__ == "__main__":
    unittest.main()
