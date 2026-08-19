import unittest

from crawler.adapters.oppo import normalize_oppo_job


class OppoAdapterTests(unittest.TestCase):
    SOURCE = {"id": "oppo-campus", "company": "OPPO", "url": "https://careers.oppo.com/university/oppo/campus/post"}

    def test_normalizes_full_time_position(self):
        job = normalize_oppo_job({
            "idRecruitPosition": 1870,
            "positionName": "新材料应用工程师",
            "positionDesc": "负责材料开发",
            "positionRequire": "材料类专业，本科及以上",
            "positionTypeName": "硬件类",
            "workCityName": "东莞市",
            "recruitmentTypeName": "应届生",
            "releaseTime": "2026-08-06",
        }, self.SOURCE)
        self.assertIsNotNone(job)
        self.assertEqual(job["job_nature"], "全职")
        self.assertEqual(job["category"], "硬件研发")
        self.assertEqual(job["degree"], "本科及以上")
        self.assertEqual(job["apply_url"], "https://careers.oppo.com/university/oppo/campus/post/1870")

    def test_normalizes_internship_and_rejects_doctor_only(self):
        intern = normalize_oppo_job({
            "idRecruitPosition": 1599, "positionName": "软件工程实习生",
            "positionDesc": "参与软件开发", "positionRequire": "熟悉 Python",
            "positionTypeName": "软件类", "workCityName": "深圳市",
            "recruitmentTypeName": "实习生",
        }, self.SOURCE)
        self.assertEqual(intern["job_nature"], "实习")
        doctor = dict(intern, idRecruitPosition=1735, positionName="研究员-博士", recruitmentTypeName="博士生")
        self.assertIsNone(normalize_oppo_job(doctor, self.SOURCE))


if __name__ == "__main__":
    unittest.main()
