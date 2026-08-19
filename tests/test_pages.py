import unittest

from fastapi.testclient import TestClient

from app.main import app


class PageSplitTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()

    def test_three_page_routes_and_responsibilities(self):
        home = self.client.get("/")
        profile = self.client.get("/profile")
        admin = self.client.get("/admin/sources")
        self.assertEqual(home.status_code, 200)
        self.assertEqual(profile.status_code, 200)
        self.assertEqual(admin.status_code, 200)
        self.assertIn("岗位工作台", home.text)
        self.assertNotIn("企业招聘入口注册表", home.text)
        self.assertNotIn("AI 结构化分析", home.text)
        self.assertIn("建立你的求职画像", profile.text)
        self.assertIn("AI 结构化分析", profile.text)
        self.assertIn("企业与岗位数据管理", admin.text)
        self.assertIn("待接入队列", admin.text)
        self.assertIn("岗位隔离证据", admin.text)

    def test_company_directory_exposes_collection_state(self):
        response = self.client.get("/api/company-job-directory")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json())
        self.assertIn("has_integrated_source", response.json()[0])
        self.assertIn("paused_reason", response.json()[0])

    def test_recommendation_endpoint_explains_missing_profile(self):
        response = self.client.get("/api/recommendations?limit=5")
        self.assertEqual(response.status_code, 200)
        self.assertIn("needs_profile", response.json())
        self.assertIn("profile_ready", response.json())


if __name__ == "__main__":
    unittest.main()
