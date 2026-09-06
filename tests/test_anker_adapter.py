import json
import unittest
from pathlib import Path

from crawler.adapters.anker import AnkerCampusAdapter


class AnkerAdapterTests(unittest.TestCase):
    def test_normalizes_public_detail_fixture(self):
        raw = json.loads((Path(__file__).parent / "fixtures" / "anker_job.json").read_text(encoding="utf-8"))
        raw["source_job_id"] = raw["id"]
        job = AnkerCampusAdapter().normalize({
            "id": "anker-campus-api", "company": "安克创新",
            "url": "https://career.anker-in.com/universities/recruitment/",
            "campus_only": True,
        }, raw)
        self.assertIsNotNone(job)
        self.assertEqual(job["company"], "安克创新")
        self.assertEqual(job["job_nature"], "全职")
        self.assertEqual(job["category"], "职能")
        self.assertIn("electronic information", job["requirements"])


if __name__ == "__main__":
    unittest.main()
