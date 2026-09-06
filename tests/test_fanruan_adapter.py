import unittest

from crawler.adapters.fanruan import normalize_fanruan_job, parse_fanruan_detail


DETAIL_HTML = """
<div class="job-title">后端开发工程师（AI团队定向）</div>
<div class="job-desc-extra"><p><span>工作地点：</span><span class="job-info">南京, 成都, 无锡</span></p></div>
<div class="job-main"><div class="job-sub-title">职位介绍</div><div class="job-sub-desc">参与企业 AI 平台建设。</div></div>
<div class="job-main"><div class="job-sub-title">岗位职责</div><div class="job-sub-desc">负责接口设计和代码实现。</div></div>
<div class="job-main"><div class="job-sub-title">岗位要求</div><div class="job-sub-desc">1. 2027届本科及以上；2. 熟悉 Python。</div></div>
<a class="detail-toudi-btn" href="https://example.com/apply/1">投递简历</a>
"""


class FanruanAdapterTests(unittest.TestCase):
    def test_parses_detail_sections_and_application(self):
        result = parse_fanruan_detail(DETAIL_HTML)
        self.assertEqual(result["detail_title"], "后端开发工程师（AI团队定向）")
        self.assertIn("接口设计", result["detail_duty"])
        self.assertIn("2027", result["detail_requirement"])
        self.assertEqual(result["detail_location"], "南京, 成都, 无锡")
        self.assertEqual(result["detail_submit"], "https://example.com/apply/1")

    def test_normalizes_only_complete_campus_job(self):
        raw = {
            "id": "9886",
            "job_name": "后端开发工程师（AI团队定向）",
            "job_type": "研发类",
            "base": "南京, 成都, 无锡",
            "mode": "校招",
            "duty": "负责接口设计和代码实现。",
            "requirement": "1. 2027届本科及以上；2. 熟悉 Python。",
            "submit": "https://example.com/apply/1",
        }
        result = normalize_fanruan_job(raw, {
            "id": "fanruan-campus",
            "company": "帆软",
            "url": "https://join.fanruan.com/campus",
        })
        self.assertEqual(result["job_nature"], "全职")
        self.assertEqual(result["graduate_year"], "2027")
        self.assertIn("成都", result["city"])
        self.assertIn("Python", result["requirements"])

    def test_rejects_missing_requirements(self):
        raw = {"id": "1", "job_name": "岗位", "mode": "校招", "duty": "职责"}
        self.assertIsNone(normalize_fanruan_job(raw, {"id": "f", "company": "帆软", "url": "https://join.fanruan.com/campus"}))


if __name__ == "__main__":
    unittest.main()
