import json
import unittest
from pathlib import Path

from crawler.adapters.apple import AppleCampusAdapter


class AppleAdapterTests(unittest.TestCase):
    def test_normalizes_explicit_intern_title(self):
        raw = json.loads((Path(__file__).parent / "fixtures" / "apple_job.json").read_text(encoding="utf-8"))
        source = {
            "id": "apple-china-intern-api",
            "company": "Apple",
            "url": "https://jobs.apple.com/zh-cn/search?location=china-mainland",
            "mode": "apple",
            "campus_only": True,
        }
        job = AppleCampusAdapter().normalize(source, raw)
        self.assertIsNotNone(job)
        self.assertEqual(job["job_nature"], "实习")
        self.assertEqual(job["source_job_id"], "PIPE-114438030")


if __name__ == "__main__":
    unittest.main()
