import unittest

from crawler.adapters.moka import normalize_moka_job

SOURCE = {
    "id": "kingsoft-campus",
    "company": "金山办公",
    "url": "https://join.wps.cn/campus-recruitment/wps/41436",
    "campus_only": True,
}


class MokaNormalizeTests(unittest.TestCase):
    def test_normalizes_concrete_moka_job(self):
        raw = {
            "source_job_id": "24d44c91-5110-4c0b-989e-9c0d4d80ba25",
            "title": "全栈开发工程师（2026届校招）",
            "nature": "全职",
            "city": "北京市",
            "description": "全栈功能开发：参与公司核心产品的前后端全流程开发。",
            "requirements": "2026届全日制本科及以上学历，计算机相关专业。",
        }
        job = normalize_moka_job(raw, SOURCE)
        self.assertIsNotNone(job)
        self.assertEqual(job["company"], "金山办公")
        self.assertEqual(job["title"], "全栈开发工程师（2026届校招）")
        self.assertEqual(job["city"], "北京")
        self.assertEqual(job["job_nature"], "全职")
        self.assertEqual(job["source_job_id"], "24d44c91-5110-4c0b-989e-9c0d4d80ba25")
        # Official campus detail route is the apply entry.
        self.assertIn("#/job/24d44c91-5110-4c0b-989e-9c0d4d80ba25", job["apply_url"])
        self.assertIn("全栈功能开发", job["description"])
        self.assertIn("2026届", job["requirements"])

    def test_intern_nature_and_city_from_list_card(self):
        raw = {
            "source_job_id": "94b1a8e3-6715-46c4-b702-5dc33c919669",
            "title": "多模态大模型算法实习生",
            "nature": "实习",
            "city": "广东·珠海市",
            "description": "负责多模态大模型算法的研究与落地。",
        }
        job = normalize_moka_job(raw, SOURCE)
        self.assertIsNotNone(job)
        self.assertEqual(job["job_nature"], "实习")
        self.assertEqual(job["city"], "珠海")
        self.assertIsNone(job["requirements"])

    def test_city_hint_fallback_from_detail_header(self):
        # List card has no city, but the detail header line carries it.
        raw = {
            "source_job_id": "8d0c42a2-99cb-4454-a8f7-662ff704b1a1",
            "title": "技术支持实习生",
            "nature": "实习",
            "city": None,
            "city_hint": "控股集团|浙江·杭州市|职能类",
            "description": "协助用户排查处理办公软件使用问题。",
        }
        job = normalize_moka_job(raw, SOURCE)
        self.assertIsNotNone(job)
        self.assertEqual(job["city"], "杭州")

    def test_rejects_without_id_or_title(self):
        self.assertIsNone(normalize_moka_job({}, SOURCE))
        self.assertIsNone(normalize_moka_job({"source_job_id": "x"}, SOURCE))
        self.assertIsNone(normalize_moka_job({"title": "no id"}, SOURCE))


if __name__ == "__main__":
    unittest.main()
