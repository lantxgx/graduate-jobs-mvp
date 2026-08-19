import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app import db
from app.main import app


class ProfileApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.previous_db_path = db.DB_PATH
        db.DB_PATH = Path(self.temp_dir.name) / "jobs.db"
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        db.DB_PATH = self.previous_db_path
        self.temp_dir.cleanup()

    def test_session_only_profile_does_not_persist_raw_resume(self):
        response = self.client.put(
            "/api/profile",
            json={"save_profile": False, "target_roles": ["Algorithm"], "raw_resume": "PRIVATE"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["saved"])
        self.assertFalse(db.get_user_profile())

    def test_saved_structured_profile_can_be_deleted(self):
        response = self.client.put(
            "/api/profile",
            json={"save_profile": True, "target_roles": ["Backend"], "skills": ["Python"]},
        )
        self.assertTrue(response.json()["saved"])
        self.assertEqual(self.client.get("/api/profile").json()["target_roles"], ["Backend"])
        self.assertTrue(self.client.delete("/api/profile").json()["deleted"])
        self.assertFalse(self.client.get("/api/profile").json().get("saved", True))

    def test_city_preference_is_soft_unless_user_selects_hard(self):
        db.init_db()
        db.upsert_job({
            "source_id": "profile-city", "job_nature": "全职", "company": "Example", "title": "Backend Engineer",
            "city": "Beijing", "source_url": "https://example.com/jobs/city", "content_hash": "profile-city-1", "raw": {},
        })
        db.save_user_profile({"target_cities": ["Shanghai"], "city_preference_mode": "preference"})
        self.assertTrue(self.client.get("/api/jobs/with-profile").json()[0]["hard_filter_pass"])
        db.save_user_profile({"target_cities": ["Shanghai"], "city_preference_mode": "hard"})
        hard_result = self.client.get("/api/jobs/with-profile").json()[0]
        self.assertFalse(hard_result["hard_filter_pass"])
        self.assertIn("outside_explicit_city_preference", hard_result["hard_filter_reasons"])

    def test_recommendation_mix_is_stored_and_returned(self):
        db.init_db()
        mix = {"main": 60, "target_company": 20, "adjacent": 15, "exploration": 5}
        response = self.client.put("/api/profile", json={"recommendation_mix": mix})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/api/profile").json()["recommendation_mix"], mix)

    def test_explicit_exclusion_is_explained_without_hiding_job(self):
        db.init_db()
        db.upsert_job(
            {
                "source_id": "fixture",
                "job_nature": "全职",
                "company": "Example",
                "title": "Sales Engineer",
                "city": "Beijing",
                "source_url": "https://example.com/jobs",
                "content_hash": "profile-fixture-1",
                "raw": {},
            }
        )
        db.save_user_profile({"excluded_roles": ["sales"], "target_cities": ["Shanghai"]})
        result = self.client.get("/api/jobs/with-profile").json()
        self.assertEqual(len(result), 1)
        self.assertFalse(result[0]["hard_filter_pass"])
        self.assertIn("explicitly_excluded_role", result[0]["hard_filter_reasons"])

    def test_recommendations_keep_four_explainable_pools(self):
        db.init_db()
        for job_id, title, company in (
            ("1", "Backend Engineer", "Example"),
            ("2", "Data Analyst", "Target Corp"),
            ("3", "Product Intern", "Other"),
            ("4", "Data Analyst", "Other"),
        ):
            db.upsert_job(
                {
                    "source_id": "fixture",
                    "job_nature": "全职",
                    "company": company,
                    "title": title,
                    "source_url": "https://example.com/jobs",
                    "content_hash": f"recommend-{job_id}",
                    "raw": {},
                }
            )
        db.save_user_profile(
            {
                "target_roles": ["backend"],
                "adjacent_roles": ["data"],
                "target_companies": ["target corp"],
                "skills": ["analyst"],
            }
        )
        result = self.client.get("/api/recommendations").json()
        self.assertEqual(set(result["pools"]), {"main", "target_company", "adjacent", "exploration"})
        self.assertEqual(result["pools"]["main"][0]["recommendation_pool"], "main")
        self.assertIn("target_company_match", result["items"][0]["recommendation_reasons"])
        self.assertIn("skill_matches", result["items"][0]["match_dimensions"])
        self.assertIn("basic_qualification", result["items"][0]["match_dimensions"])
        self.assertIn("ability_match", result["items"][0]["match_dimensions"])
        self.assertIn("transition_distance", result["items"][0]["match_dimensions"])
        self.assertTrue(result["items"][0]["recall_channels"])
        self.assertIn(result["items"][0]["competition_risk"], {"low", "medium", "high"})
        self.assertTrue(result["items"][0]["competition_risk_basis"])
        self.assertTrue(result["pools"]["adjacent"][0]["adjacent_explanation"])

    def test_ignore_is_soft_for_search_but_excludes_default_recommendations(self):
        db.init_db()
        db.upsert_job({
            "source_id": "fixture", "job_nature": "全职", "company": "Example", "title": "Backend Engineer",
            "source_url": "https://example.com/jobs", "content_hash": "ignore-fixture-1", "raw": {},
        })
        with db.connect() as conn:
            job_id = conn.execute("SELECT id FROM jobs WHERE content_hash=?", ("ignore-fixture-1",)).fetchone()[0]
        db.save_user_profile({"target_roles": ["backend"]})
        self.assertEqual(len(self.client.get("/api/jobs").json()), 1)
        self.client.post(f"/api/jobs/{job_id}/action", json={"action": "ignore"})
        self.assertEqual(len(self.client.get("/api/jobs").json()), 1)
        self.assertEqual(self.client.get("/api/recommendations").json()["total_eligible"], 0)

    def test_job_action_can_be_toggled(self):
        db.init_db()
        job_id = db.upsert_job(
            {
                "source_id": "fixture",
                "job_nature": "全职",
                "company": "Example",
                "title": "Backend Engineer",
                "source_url": "https://example.com/jobs",
                "content_hash": "action-fixture-1",
                "raw": {},
            }
        )
        # Resolve the inserted integer id without coupling the test to insert order.
        with db.connect() as conn:
            row_id = conn.execute("SELECT id FROM jobs WHERE content_hash=?", ("action-fixture-1",)).fetchone()[0]
        self.assertEqual(self.client.post(f"/api/jobs/{row_id}/action", json={"action": "favorite"}).status_code, 200)
        self.assertEqual(len(self.client.get("/api/job-actions").json()), 1)
        favorite_rows = self.client.get("/api/job-actions?action=favorite").json()
        self.assertEqual([row["job_id"] for row in favorite_rows], [row_id])
        self.client.post(f"/api/jobs/{row_id}/action", json={"action": "favorite", "enabled": False})
        self.assertEqual(len(self.client.get("/api/job-actions").json()), 0)


if __name__ == "__main__":
    unittest.main()
