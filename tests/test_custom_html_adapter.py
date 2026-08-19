import unittest
from pathlib import Path

from crawler.adapters.custom_html import parse_visible_job_cards


ROOT = Path(__file__).parent / "fixtures" / "custom-html-campus"


class CustomHtmlAdapterTests(unittest.TestCase):
    SOURCE = {"id": "custom-html", "company": "Example", "url": "https://careers.example.com/jobs"}

    def test_visible_cards_require_explicit_fields_and_links(self):
        html = (ROOT / "listing.html").read_text(encoding="utf-8")
        jobs = parse_visible_job_cards(html, self.SOURCE, max_jobs=20)
        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs[0]["title"], "Backend Engineering Intern")
        self.assertEqual(jobs[0]["city"], "Shanghai")
        self.assertEqual(jobs[0]["apply_url"], "https://careers.example.com/jobs/custom-101")
        self.assertEqual(jobs[1]["job_nature"], "全职")

    def test_navigation_card_and_unknown_type_are_rejected(self):
        html = (ROOT / "listing.html").read_text(encoding="utf-8")
        jobs = parse_visible_job_cards(html, self.SOURCE, max_jobs=20)
        titles = {job["title"] for job in jobs}
        self.assertNotIn("Campus program", titles)
        self.assertNotIn("Unclear hiring type", titles)


if __name__ == "__main__":
    unittest.main()
