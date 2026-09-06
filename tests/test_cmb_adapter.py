import unittest

from crawler.adapters.cmb import CmbCampusAdapter


class CmbAdapterTests(unittest.TestCase):
    def test_normalize_detail(self):
        source = {
            "id": "cmb-campus-roster", "company": "招商银行",
            "url": "https://career.cmbchina.com/positionlist",
            "recruitment_type_id": "DF94FD6D-26D3-4A19-9E69-577C4BA1DE82",
        }
        raw = {"listing": {"publishGID": "demo", "jobDisplay": "研究院实习生", "locationName": "深圳市"},
               "detail": {"publishGID": "demo", "jobDisplay": "研究院实习生", "locationName": "深圳市",
                          "jobResponsibility": "<p>协助研究。</p>", "jobRequirement": "<p>硕士及以上学历。</p>"}}
        job = CmbCampusAdapter().normalize(source, raw)
        self.assertEqual(job["company"], "招商银行")
        self.assertEqual(job["job_nature"], "实习")
        self.assertIn("协助研究", job["description"])


if __name__ == "__main__":
    unittest.main()
