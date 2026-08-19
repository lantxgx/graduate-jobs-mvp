import json
import unittest
from pathlib import Path

from crawler.adapters.lever import normalize_lever_job
from crawler.normalize import JOB_NATURE_FULL_TIME, JOB_NATURE_INTERNSHIP


ROOT = Path(__file__).parent / "fixtures" / "lever-campus"


class LeverAdapterTests(unittest.TestCase):
    SOURCE = {"id": "lever-example", "company": "Example", "url": "https://jobs.lever.co/example"}

    def test_public_feed_normalizes_explicit_commitment_and_urls(self):
        rows = json.loads((ROOT / "listing.json").read_text(encoding="utf-8"))
        internship = normalize_lever_job(rows[0], self.SOURCE)
        full_time = normalize_lever_job(rows[1], self.SOURCE)
        self.assertEqual(internship["job_nature"], JOB_NATURE_INTERNSHIP)
        self.assertEqual(full_time["job_nature"], JOB_NATURE_FULL_TIME)
        self.assertEqual(internship["city"], "Shanghai / China")
        self.assertEqual(internship["apply_url"], "https://jobs.lever.co/example/lever-001/apply")
        self.assertIn("Python", internship["description"])

    def test_missing_apply_url_is_rejected(self):
        raw = {"id": "missing", "text": "Intern", "categories": {"commitment": "Internship"}, "descriptionPlain": "Build tools."}
        self.assertIsNone(normalize_lever_job(raw, self.SOURCE))

    def test_unknown_commitment_is_rejected(self):
        raw = {"id": "unknown", "text": "Engineer", "categories": {}, "descriptionPlain": "Build tools.", "applyUrl": "https://jobs.lever.co/example/unknown"}
        self.assertIsNone(normalize_lever_job(raw, self.SOURCE))


if __name__ == "__main__":
    unittest.main()
