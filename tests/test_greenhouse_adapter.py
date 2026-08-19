import json
import unittest
from pathlib import Path

from crawler.adapters.greenhouse import normalize_greenhouse_job
from crawler.normalize import JOB_NATURE_FULL_TIME, JOB_NATURE_INTERNSHIP


ROOT = Path(__file__).parent / "fixtures" / "greenhouse-campus"


class GreenhouseAdapterTests(unittest.TestCase):
    SOURCE = {
        "id": "greenhouse-example",
        "company": "Example",
        "url": "https://boards.greenhouse.io/example",
    }

    def test_public_record_normalizes_explicit_fields(self):
        payload = json.loads((ROOT / "listing.json").read_text(encoding="utf-8"))
        internship = normalize_greenhouse_job(payload["jobs"][0], self.SOURCE)
        full_time = normalize_greenhouse_job(payload["jobs"][1], self.SOURCE)
        self.assertEqual(internship["job_nature"], JOB_NATURE_INTERNSHIP)
        self.assertEqual(full_time["job_nature"], JOB_NATURE_FULL_TIME)
        self.assertEqual(internship["city"], "Shanghai")
        self.assertEqual(internship["apply_url"], "https://boards.greenhouse.io/example/jobs/88101")
        self.assertIn("Python", internship["description"])

    def test_missing_absolute_url_is_rejected_without_guessing(self):
        raw = {"id": 1, "title": "Software Engineering Intern", "employment_type": "Internship", "content": "Build tools."}
        self.assertIsNone(normalize_greenhouse_job(raw, self.SOURCE))

    def test_unknown_recruitment_type_is_rejected(self):
        raw = {"id": 2, "title": "Software Engineer", "absolute_url": "https://example/jobs/2", "content": "Build tools."}
        self.assertIsNone(normalize_greenhouse_job(raw, self.SOURCE))

    def test_non_http_detail_url_is_rejected(self):
        raw = {"id": 3, "title": "Software Engineering Intern", "employment_type": "Internship", "absolute_url": "javascript:void(0)", "content": "Build tools."}
        self.assertIsNone(normalize_greenhouse_job(raw, self.SOURCE))


if __name__ == "__main__":
    unittest.main()
