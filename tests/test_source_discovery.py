import tempfile
import unittest
from pathlib import Path

from crawler.source_discovery import classify_ats, import_company_candidates, make_candidate, verify_official_ownership


class SourceDiscoveryTests(unittest.TestCase):
    def test_classifies_common_ats_domains(self):
        self.assertEqual(classify_ats("https://acme.jobs.feishu.cn/campus"), "feishu")
        self.assertEqual(classify_ats("https://acme.zhiye.com/jobs"), "beisen")
        self.assertEqual(classify_ats("https://jobs.ashbyhq.com/acme"), "ashby")
        self.assertEqual(classify_ats("https://careers.acme.example/jobs"), "custom")

    def test_official_ownership_is_conservative(self):
        company = {"canonical_name": "Acme", "official_website": "https://www.acme.example"}
        self.assertTrue(verify_official_ownership(company, {
            "url": "https://careers.acme.example/jobs",
            "evidence_url": "https://www.acme.example/careers",
        }))
        self.assertFalse(verify_official_ownership(company, {
            "url": "https://unknown.example/jobs",
            "evidence_url": "https://search.example/result",
        }))

    def test_imports_candidate_csv_without_creating_jobs(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "companies.csv"
            path.write_text(
                "canonical_name,brand_name,official_website\nAcme,Acme,https://acme.example\n",
                encoding="utf-8",
            )
            rows = import_company_candidates(path)
            self.assertEqual(rows[0]["canonical_name"], "Acme")
            candidate = make_candidate(rows[0], "https://careers.acme.example/jobs", "https://acme.example/careers", "manual")
            self.assertEqual(candidate.official_status, "confirmed")


if __name__ == "__main__":
    unittest.main()
