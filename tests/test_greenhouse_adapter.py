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

    def test_requirements_heading_is_split_from_greenhouse_content(self):
        raw = {
            "id": 4,
            "title": "Software Engineering Intern",
            "employment_type": "Internship",
            "absolute_url": "https://example/jobs/4",
            "content": "Build useful tools. We'd love to hear from you if you have: Python experience.",
        }
        job = normalize_greenhouse_job(raw, self.SOURCE)
        self.assertIn("Build useful tools", job["description"])
        self.assertIn("Python experience", job["requirements"])

    def test_requirements_heading_without_colon_is_split(self):
        raw = {
            "id": 5,
            "title": "Business Analyst (New Grad)",
            "employment_type": "Full-time",
            "absolute_url": "https://example/jobs/5",
            "content": "Analyze business data. What you bring\nStrong analytical skills.",
        }
        job = normalize_greenhouse_job(raw, self.SOURCE)
        self.assertIn("Analyze business data", job["description"])
        self.assertIn("Strong analytical skills", job["requirements"])

    def test_requirements_heading_who_you_are_is_split(self):
        raw = {
            "id": 6,
            "title": "Product Management Intern",
            "employment_type": "Internship",
            "absolute_url": "https://example/jobs/6",
            "content": "Build product insights. Who You Are: Strong communication skills.",
        }
        job = normalize_greenhouse_job(raw, self.SOURCE)
        self.assertIn("Build product insights", job["description"])
        self.assertIn("Strong communication skills", job["requirements"])

    def test_requirements_heading_about_you_is_split(self):
        raw = {
            "id": 7,
            "title": "Software Engineer, AI Platform - New Grad",
            "employment_type": "Full-time",
            "absolute_url": "https://example/jobs/7",
            "content": "Build autonomy infrastructure. About You: Graduating by December 2026.",
        }
        job = normalize_greenhouse_job(raw, self.SOURCE)
        self.assertIn("Build autonomy infrastructure", job["description"])
        self.assertIn("Graduating by December 2026", job["requirements"])

    def test_unknown_recruitment_type_is_rejected(self):
        raw = {"id": 2, "title": "Software Engineer", "absolute_url": "https://example/jobs/2", "content": "Build tools."}
        self.assertIsNone(normalize_greenhouse_job(raw, self.SOURCE))

    def test_non_http_detail_url_is_rejected(self):
        raw = {"id": 3, "title": "Software Engineering Intern", "employment_type": "Internship", "absolute_url": "javascript:void(0)", "content": "Build tools."}
        self.assertIsNone(normalize_greenhouse_job(raw, self.SOURCE))


if __name__ == "__main__":
    unittest.main()
