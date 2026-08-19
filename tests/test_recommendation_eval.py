import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app import db
from app.main import app


class RecommendationEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.previous_db_path = db.DB_PATH
        db.DB_PATH = Path(self.temp_dir.name) / "jobs.db"
        self.client = TestClient(app)
        db.init_db()

    def tearDown(self):
        self.client.close()
        db.DB_PATH = self.previous_db_path
        self.temp_dir.cleanup()

    def add_job(self, key, title, company="Example", city="Beijing"):
        db.upsert_job({
            "source_id": "evaluation",
            "job_nature": "全职",
            "company": company,
            "title": title,
            "city": city,
            "job_nature": "Graduate",
            "description": f"Responsibilities for {title}",
            "requirements": "Bachelor degree",
            "source_url": "https://example.com/jobs",
            "apply_url": f"https://example.com/jobs/{key}",
            "content_hash": f"evaluation-{key}",
            "raw": {},
        })

    def profile(self, **values):
        db.save_user_profile(values)

    def test_sales_volume_does_not_displace_algorithm_main_pool(self):
        self.add_job("algorithm", "Algorithm Engineer")
        for index in range(20):
            self.add_job(f"sales-{index}", "Sales Representative")
        self.profile(target_roles=["algorithm"])
        result = self.client.get("/api/recommendations").json()
        main_titles = [job["title"] for job in result["pools"]["main"]]
        self.assertIn("Algorithm Engineer", main_titles)
        self.assertNotIn("Sales Representative", main_titles)

    def test_explicit_target_company_is_a_separate_recall_channel(self):
        self.add_job("target", "Product Manager", company="Wanted Corp")
        self.profile(target_roles=["algorithm"], target_companies=["wanted corp"])
        result = self.client.get("/api/recommendations").json()
        self.assertTrue(any(job["company"] == "Wanted Corp" for job in result["pools"]["target_company"]))

    def test_high_competition_does_not_remove_main_role(self):
        self.add_job("hard", "Algorithm Engineer")
        self.profile(target_roles=["algorithm"])
        result = self.client.get("/api/recommendations").json()
        job = next(job for job in result["pools"]["main"] if job["title"] == "Algorithm Engineer")
        self.assertEqual(job["competition_risk"], "high")
        self.assertEqual(job["match_dimensions"]["transition_distance"]["status"], "direct")

    def test_missing_graduation_year_is_not_a_hard_exclusion(self):
        self.add_job("year-unknown", "Backend Engineer")
        self.profile(education="Bachelor")
        result = self.client.get("/api/jobs/with-profile").json()
        self.assertTrue(result[0]["hard_filter_pass"])

    def test_explicit_sales_exclusion_preserves_all_jobs_but_not_recommendations(self):
        self.add_job("sales-excluded", "Sales Representative")
        self.add_job("backend-kept", "Backend Engineer")
        self.profile(target_roles=["backend"], excluded_roles=["sales"])
        self.assertEqual(len(self.client.get("/api/jobs").json()), 2)
        result = self.client.get("/api/recommendations").json()
        self.assertFalse(any("Sales" in job["title"] for job in result["items"]))

    def test_thirty_case_regression_matrix(self):
        """Run five variants of each high-risk product gate as executable offline cases."""
        cases = []
        for index in range(5):
            cases.extend([
                {"name": f"sales-volume-{index}", "kind": "sales_volume"},
                {"name": f"target-company-{index}", "kind": "target_company"},
                {"name": f"competition-{index}", "kind": "competition"},
                {"name": f"missing-year-{index}", "kind": "missing_year"},
                {"name": f"sales-exclusion-{index}", "kind": "sales_exclusion"},
                {"name": f"explanation-{index}", "kind": "explanation"},
            ])
        self.assertEqual(len(cases), 30)
        original_db_path = db.DB_PATH
        try:
            for case in cases:
                db.DB_PATH = self.temp_dir.name and Path(self.temp_dir.name) / f"{case['name']}.db"
                db.init_db()
                kind = case["kind"]
                if kind == "sales_volume":
                    self.add_job(case["name"] + "-algorithm", "Algorithm Engineer")
                    for sales_index in range(8):
                        self.add_job(f"{case['name']}-sales-{sales_index}", "Sales Representative")
                    self.profile(target_roles=["algorithm"])
                    result = self.client.get("/api/recommendations").json()
                    self.assertTrue(any(job["title"] == "Algorithm Engineer" for job in result["pools"]["main"]))
                    self.assertFalse(any(job["title"] == "Sales Representative" for job in result["pools"]["main"]))
                elif kind == "target_company":
                    self.add_job(case["name"], "Product Manager", company="Wanted Corp")
                    self.profile(target_roles=["algorithm"], target_companies=["wanted corp"])
                    result = self.client.get("/api/recommendations").json()
                    self.assertTrue(any(job["company"] == "Wanted Corp" for job in result["pools"]["target_company"]))
                elif kind == "competition":
                    self.add_job(case["name"], "Algorithm Engineer")
                    self.profile(target_roles=["algorithm"])
                    result = self.client.get("/api/recommendations").json()
                    job = result["pools"]["main"][0]
                    self.assertEqual(job["competition_risk"], "high")
                    self.assertEqual(job["match_dimensions"]["transition_distance"]["status"], "direct")
                elif kind == "missing_year":
                    self.add_job(case["name"], "Backend Engineer")
                    self.profile(education="Bachelor")
                    self.assertTrue(self.client.get("/api/jobs/with-profile").json()[0]["hard_filter_pass"])
                elif kind == "sales_exclusion":
                    self.add_job(case["name"] + "-sales", "Sales Representative")
                    self.add_job(case["name"] + "-backend", "Backend Engineer")
                    self.profile(target_roles=["backend"], excluded_roles=["sales"])
                    self.assertEqual(len(self.client.get("/api/jobs").json()), 2)
                    result = self.client.get("/api/recommendations").json()
                    self.assertFalse(any("Sales" in job["title"] for job in result["items"]))
                else:
                    self.add_job(case["name"], "Data Analyst")
                    self.profile(target_roles=["algorithm"], adjacent_roles=["data"], skills=["python"])
                    result = self.client.get("/api/recommendations").json()
                    job = result["items"][0]
                    self.assertTrue(job["recall_channels"])
                    for key in ("basic_qualification", "ability_match", "job_seeking_intent", "company_preference", "transition_distance", "confidence"):
                        self.assertIn(key, job["match_dimensions"])
        finally:
            db.DB_PATH = original_db_path


if __name__ == "__main__":
    unittest.main()
