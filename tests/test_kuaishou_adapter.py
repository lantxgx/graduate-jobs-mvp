import json
import unittest
from pathlib import Path

from crawler.adapters.kuaishou import KuaishouCampusAdapter


class KuaishouAdapterTests(unittest.TestCase):
    def test_normalizes_public_position_fixture(self):
        fixture = Path(__file__).parent / "fixtures" / "kuaishou_position.json"
        raw = json.loads(fixture.read_text(encoding="utf-8"))
        source = {
            "id": "kuaishou-campus-roster",
            "company": "快手",
            "url": "https://campus.kuaishou.cn",
            "campus_only": True,
        }
        job = KuaishouCampusAdapter().normalize(source, raw)
        self.assertIsNotNone(job)
        self.assertEqual(job["source_job_id"], "13101")
        self.assertEqual(job["job_nature"], "全职")
        self.assertEqual(job["city"], "北京 / 杭州")
        self.assertEqual(job["degree"], "硕士及以上")
        self.assertIn("job-info/13101", job["apply_url"])


if __name__ == "__main__":
    unittest.main()
