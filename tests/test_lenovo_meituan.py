import unittest

from crawler.adapters.lenovo import normalize_lenovo_job
from crawler.adapters.meituan import normalize_meituan_job


class NewSourceAdapterTests(unittest.TestCase):
    def test_lenovo_maps_codes_and_detail_route(self):
        job = normalize_lenovo_job(
            {"id": 2362, "jobName": "AI role", "workPlace": "1,6", "typeName": "技术研究类", "jobDuties": "duties", "jobRequirement": "本科"},
            {"id": "lenovo-campus", "company": "Lenovo", "url": "https://talent.lenovo.com.cn/position?projectType=1"},
        )
        self.assertEqual(job["job_nature"], "全职")
        self.assertEqual(job["city"], "北京 / 天津")
        self.assertIn("/position/detail?id=2362", job["apply_url"])

    def test_meituan_uses_stable_union_id_and_internship_type(self):
        job = normalize_meituan_job(
            {"jobUnionId": "m1", "name": "Data intern", "jobType": "2", "cityList": [{"name": "北京市"}], "jobDuty": "duties", "jobRequirement": "本科"},
            {"id": "meituan-campus", "company": "Meituan", "url": "https://zhaopin.meituan.com/web/position?hiringType=4_1"},
        )
        self.assertEqual(job["source_job_id"], "m1")
        self.assertEqual(job["job_nature"], "实习")
        self.assertEqual(job["city"], "北京市")
        self.assertTrue(job["apply_url"].startswith("https://zhaopin.meituan.com/"))


if __name__ == "__main__":
    unittest.main()
