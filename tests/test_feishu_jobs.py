import unittest

from crawler.feishu_jobs import parse_feishu_detail_text
from crawler.normalize import normalize_job


class FeishuJobsTest(unittest.TestCase):
    def test_parse_detail_text(self):
        text = """【27届校招】备件计划培训生
广州正式生产 / 制造 / 加工 - 汽车销售与服务
职位描述
1、制定补库计划。
2、优化库存结构。
职位要求
1、本科及以上学历。
2、具备数据分析能力。
投递
"""
        job = parse_feishu_detail_text(
            text,
            "https://xiaopeng.jobs.feishu.cn/campus/position/7673466913318619401/detail",
        )
        self.assertIsNotNone(job)
        self.assertEqual(job["id"], "7673466913318619401")
        self.assertEqual(job["title"], "【27届校招】备件计划培训生")
        self.assertEqual(job["city"], "广州")
        self.assertEqual(job["recruitment_type"], "正式")
        self.assertEqual(
            job["category"], "生产 / 制造 / 加工 - 汽车销售与服务"
        )
        self.assertIn("制定补库计划", job["description"])
        self.assertIn("本科及以上学历", job["requirements"])

        normalized = normalize_job(
            job,
            {
                "id": "xiaopeng-campus",
                "company": "小鹏集团",
                "url": "https://xiaopeng.jobs.feishu.cn/campus/position/list",
                "campus_only": True,
            },
        )
        self.assertEqual(normalized["job_nature"], "全职")

    def test_same_parser_supports_second_feishu_company_shape(self):
        text = """Graduate Software Engineer
Shanghai \u6b63\u5f0f Software R&D
\u804c\u4f4d\u63cf\u8ff0
Build internal tools and services.
\u804c\u4f4d\u8981\u6c42
Bachelor degree or above; Java or Go experience.
\u6295\u9012"""
        job = parse_feishu_detail_text(
            text,
            "https://second-company.jobs.feishu.cn/campus/position/9000000000000000001/detail",
        )
        self.assertIsNotNone(job)
        self.assertEqual(job["id"], "9000000000000000001")
        self.assertEqual(job["city"], "Shanghai")
        self.assertEqual(job["recruitment_type"], "\u6b63\u5f0f")


if __name__ == "__main__":
    unittest.main()
