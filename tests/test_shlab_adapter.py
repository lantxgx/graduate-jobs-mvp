import json
import unittest
from pathlib import Path

from crawler.adapters.shlab import ShlabCampusAdapter, _item_to_raw


class ShlabAdapterTests(unittest.TestCase):
    def test_normalizes_public_campus_api_item(self):
        item = json.loads((Path(__file__).parent / "fixtures" / "shlab_job.json").read_text(encoding="utf-8"))
        source = {
            "id": "shlab-campus",
            "company": "上海人工智能实验室",
            "url": "https://www.shlab.org.cn/joinus/campus?mode=campus",
            "campus_only": True,
        }
        job = ShlabCampusAdapter().normalize(source, _item_to_raw(item, source))
        self.assertIsNotNone(job)
        self.assertEqual(job["city"], "上海")
        self.assertEqual(job["job_nature"], "实习")
        self.assertEqual(job["source_job_id"], "7681244051312134427")
        self.assertIn("joinus/detail", job["apply_url"])


if __name__ == "__main__":
    unittest.main()
