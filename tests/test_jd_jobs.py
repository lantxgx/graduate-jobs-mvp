import unittest

from crawler.adapters.jd import normalize_jd_job


class JdAdapterTests(unittest.TestCase):
    def setUp(self):
        self.source = {"id": "source-6d787af3a9ff8ba3", "company": "京东", "url": "https://campus.jd.com"}

    def test_normalizes_public_full_time_detail(self):
        job = normalize_jd_job({"publishId": 9257, "positionName": "营业部/集配站站长", "recruitType": "应届生", "jobCategory": "物流储备类", "workContent": "负责物流运营。", "qualification": "2027年毕业，统招本科及以上学历。", "requirementVoList": [{"workCity": "吉林省-长春市"}]}, self.source)
        self.assertEqual(job["job_nature"], "全职")
        self.assertEqual(job["city"], "吉林省-长春市")
        self.assertEqual(job["degree"], "本科及以上")
        self.assertEqual(job["graduate_year"], "2027")
        self.assertIn("details?id=9257", job["apply_url"])

    def test_normalizes_internship_detail(self):
        job = normalize_jd_job({"publishId": 4864, "positionName": "物流运营", "recruitType": "实习生", "jobCategory": "采销与物流方向", "workContent": "参与物流运营。", "qualification": "本科在校生，27届优先。", "requirementVoList": [{"workCity": "北京市-北京市"}]}, self.source)
        self.assertEqual(job["job_nature"], "实习")
        self.assertEqual(job["degree"], "本科及以上")


if __name__ == "__main__":
    unittest.main()
