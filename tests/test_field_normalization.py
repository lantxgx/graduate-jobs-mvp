import unittest

from crawler.normalize import (
    extract_major_requirements,
    normalize_category,
    normalize_city,
    normalize_degree,
    normalize_job_nature,
    split_location_records,
)


class FieldNormalizationTests(unittest.TestCase):
    def test_recruitment_type_is_only_full_time_or_internship(self):
        self.assertEqual(normalize_job_nature("校招 / 实习", "算法实习生"), "实习")
        self.assertEqual(normalize_job_nature("正式", "软件工程师"), "全职")
        self.assertEqual(normalize_job_nature("Graduate", "Software Engineer"), "全职")
        self.assertIsNone(normalize_job_nature("社会招聘", "Software Engineer"))
        self.assertIsNone(normalize_job_nature("其他", "Software Engineer"))

    def test_degree_is_normalized_without_inventing_a_requirement(self):
        self.assertEqual(normalize_degree("Bachelor degree or above"), "本科及以上")
        self.assertEqual(normalize_degree("硕士优先", "本科及以上"), "硕士及以上")
        self.assertEqual(normalize_degree(None, "欢迎不同学历候选人"), "未注明")

    def test_category_and_city_are_stable(self):
        self.assertEqual(normalize_category(None, "Python 后端开发工程师"), "软件研发")
        self.assertEqual(normalize_category(None, "算法工程师"), "算法/AI")
        self.assertEqual(normalize_category("算法/AI", "AI Talent Partner（招聘与运营）"), "职能")
        self.assertEqual(normalize_city("工作地点：北京 / 北京, 上海"), "北京 / 上海")

    def test_location_hierarchy_preserves_evidence_without_combining_cities(self):
        self.assertEqual(
            split_location_records("北京市-北京市 / 广东省-深圳市 / 英国-伦敦"),
            [
                {"country": "中国", "province": "北京", "city": "北京"},
                {"country": "中国", "province": "广东", "city": "深圳"},
                {"country": "英国", "province": "", "city": "伦敦"},
            ],
        )
        self.assertEqual(
            split_location_records("Shanghai / China"),
            [{"country": "中国", "province": "", "city": "Shanghai"}],
        )

    def test_academic_major_is_separate_from_job_function(self):
        requirements = "计算机、信息工程、人工智能、自动化、软件工程、数学等相关专业；有产品意识优先"
        self.assertEqual(
            extract_major_requirements(requirements),
            ["计算机类", "软件工程", "人工智能", "信息工程", "自动化类", "数学类"],
        )
        self.assertNotIn("产品", extract_major_requirements(requirements))


if __name__ == "__main__":
    unittest.main()
