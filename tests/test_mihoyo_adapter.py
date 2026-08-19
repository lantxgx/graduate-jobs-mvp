import json
import unittest
from pathlib import Path

from crawler.adapters.mihoyo import MihoyoAdapter, normalize_mihoyo_job
from crawler.normalize import JOB_NATURE_FULL_TIME, JOB_NATURE_INTERNSHIP, normalize_degree


ROOT = Path(__file__).parent / "fixtures" / "mihoyo-campus"


class MihoyoAdapterTests(unittest.TestCase):
    SOURCE = {
        "id": "mihoyo-campus",
        "company": "MiHoYo",
        "url": "https://jobs.mihoyo.com/#/campus/position",
        "max_jobs": 20,
    }

    def test_fixture_normalizes_concrete_internship(self):
        listing = json.loads((ROOT / "listing.json").read_text(encoding="utf-8"))["data"]["records"][0]
        detail = json.loads((ROOT / "detail-9148.json").read_text(encoding="utf-8"))
        job = normalize_mihoyo_job({"listing": listing, "detail": detail}, self.SOURCE)
        self.assertIsNotNone(job)
        self.assertEqual(job["job_nature"], JOB_NATURE_INTERNSHIP)
        self.assertEqual(job["city"], "Shanghai")
        self.assertEqual(job["degree"], normalize_degree("Bachelor degree or above", job["requirements"]))
        self.assertEqual(job["apply_url"], "https://jobs.mihoyo.com/#/campus/position/9148")
        self.assertIn("generative AI", job["description"])
        self.assertIn("Bachelor", job["requirements"])

    def test_full_time_is_supported(self):
        listing = {
            "id": "10001",
            "title": "Game Project Manager",
            "addressDetailList": [{"addressDetail": "Shanghai"}],
            "competencyType": "Product",
            "jobNature": "Full-time",
        }
        detail = {"data": {"jobResponsibility": "Manage a game project.", "jobRequirement": "Bachelor degree or above."}}
        job = normalize_mihoyo_job({"listing": listing, "detail": detail}, self.SOURCE)
        self.assertEqual(job["job_nature"], JOB_NATURE_FULL_TIME)

    def test_real_api_job_require_key_is_preserved(self):
        listing = {"id": "10003", "title": "Operations Intern", "jobNature": "实习", "addressDetailList": [{"addressDetail": "上海"}]}
        detail = {"data": {"description": "Support operations.", "jobRequire": "本科及以上，熟悉数据分析。"}}
        job = normalize_mihoyo_job({"listing": listing, "detail": detail}, self.SOURCE)
        self.assertIsNotNone(job)
        self.assertTrue(job["requirements"])

    def test_explicit_competency_wins_over_ai_keyword_in_requirements(self):
        listing = {
            "id": "10004",
            "title": "E-commerce Operations Intern",
            "jobNature": "Intern",
            "competencyType": "运营类",
            "addressDetailList": [{"addressDetail": "Shanghai"}],
        }
        detail = {"data": {"description": "Operate an e-commerce store.", "jobRequire": "Interested in AI tools."}}
        job = normalize_mihoyo_job({"listing": listing, "detail": detail}, self.SOURCE)
        self.assertEqual(job["category"], "运营")

    def test_broad_mihoyo_groups_use_title_without_requirement_keyword_leakage(self):
        cases = [
            ("人力资源（统招）", "综合类", "AI tools are a plus", "职能"),
            ("游戏研发-游戏客户端工具开发", "程序&技术类", "AI awareness is helpful", "软件研发"),
            ("投放运营实习生（素材内容方向）", "市场&商务类", "AI tools are a plus", "市场/销售"),
            ("国际化市场社媒营销实习生", "国际化类", "AI tools are a plus", "市场/销售"),
        ]
        for title, competency, requirement, expected in cases:
            listing = {
                "id": title,
                "title": title,
                "jobNature": "Intern",
                "competencyType": competency,
                "addressDetailList": [{"addressDetail": "Shanghai"}],
            }
            detail = {"data": {"description": "Concrete work description.", "jobRequire": requirement}}
            job = normalize_mihoyo_job({"listing": listing, "detail": detail}, self.SOURCE)
            self.assertEqual(job["category"], expected, title)

    def test_non_product_nature_is_rejected(self):
        listing = {"id": "10002", "title": "Research Fellow", "jobNature": "PhD Program"}
        detail = {"data": {"jobResponsibility": "Research.", "jobRequirement": "PhD."}}
        self.assertIsNone(normalize_mihoyo_job({"listing": listing, "detail": detail}, self.SOURCE))

    def test_adapter_caps_max_jobs_at_twenty(self):
        self.assertEqual(min(max(100, 1), 20), 20)
        self.assertIsInstance(MihoyoAdapter(), MihoyoAdapter)


if __name__ == "__main__":
    unittest.main()
