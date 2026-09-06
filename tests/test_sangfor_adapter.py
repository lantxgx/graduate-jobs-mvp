import unittest

from crawler.adapters.sangfor import normalize_sangfor_job


class SangforAdapterTests(unittest.TestCase):
    def test_normalizes_public_campus_record(self):
        raw = {
            "positionId": 4554,
            "title": "深信服27届-技术研发工程师（AI潜力方向）",
            "description": "<p>岗位职责</p><p>参与产品研发。</p><p>岗位要求</p><p>计算机相关专业，具备编程能力。</p>",
            "commitment": "全职",
            "education": "本科",
            "functionName": "开发类",
            "workPlaceText": "深圳市,长沙市",
            "openedAt": "2026-08-07 00:00:00",
        }
        result = normalize_sangfor_job(raw, {
            "id": "sangfor-custom-campus",
            "company": "深信服",
            "url": "https://hr.sangfor.com/campucompon/schoolRecruitment",
        })
        self.assertEqual(result["source_job_id"], "4554")
        self.assertEqual(result["job_nature"], "全职")
        self.assertIn("深圳", result["city"])
        self.assertIn("编程能力", result["requirements"])

    def test_rejects_record_without_explicit_requirements(self):
        raw = {"positionId": 1, "title": "岗位", "description": "<p>只有职责</p>", "commitment": "全职", "workPlaceText": "深圳市"}
        self.assertIsNone(normalize_sangfor_job(raw, {"id": "s", "company": "深信服", "url": "https://hr.sangfor.com"}))


if __name__ == "__main__":
    unittest.main()
