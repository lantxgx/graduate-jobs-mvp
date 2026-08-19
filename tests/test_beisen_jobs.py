import unittest

from crawler.beisen_jobs import parse_beisen_payload
from crawler.browser_discovery import blocked_signal
from crawler.runner import is_qualified_job


SOURCE = {
    "id": "beisen-fixture",
    "company": "Fixture Company",
    "url": "https://fixture.zhiye.com/campus/jobs",
    "campus_only": True,
}


class BeisenAdapterTests(unittest.TestCase):
    def test_generic_discovery_stops_on_block_signals(self):
        self.assertEqual(blocked_signal(403), "HTTP 403")
        self.assertEqual(blocked_signal(429), "HTTP 429")
        self.assertIn("captcha", blocked_signal(200, "captcha required"))
        self.assertIsNone(blocked_signal(200, "ordinary job list"))

    def test_navigation_cards_are_not_concrete_jobs(self):
        self.assertEqual(parse_beisen_payload({"data": {"list": [{
            "id": "campus", "title": "校园招聘", "url": "/campus"
        }]}}, SOURCE), [])

    def test_quality_gate_rejects_non_concrete_position(self):
        self.assertFalse(is_qualified_job({"title": "校园招聘", "apply_url": "https://example.com/campus"}))

    def test_normalizes_common_beisen_aliases(self):
        payload = {
            "data": {
                "list": [
                    {
                        "jobId": "360-001",
                        "jobName": "Algorithm Engineer",
                        "workCity": "Beijing",
                        "jobType": "Graduate",
                        "jobCategory": "Algorithm/AI",
                        "education": "Master",
                        "jobDescription": "Build ranking models",
                        "jobRequirements": "Python and machine learning",
                        "detailUrl": "/job/360-001",
                    }
                ]
            }
        }
        jobs = parse_beisen_payload(payload, SOURCE)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["source_job_id"], "360-001")
        self.assertEqual(jobs[0]["city"], "Beijing")
        self.assertEqual(jobs[0]["apply_url"], "https://fixture.zhiye.com/job/360-001")

    def test_deduplicates_same_position_across_payloads(self):
        payload = [
            {"id": "a", "title": "QA Engineer", "city": "Shanghai", "url": "/job/a"},
            {"id": "a", "title": "QA Engineer", "city": "Shanghai", "url": "/job/a"},
        ]
        jobs = parse_beisen_payload(payload, SOURCE)
        self.assertEqual(len(jobs), 1)

    def test_360_style_fields_require_an_explicit_detail_url(self):
        concrete = {
            "JobAdId": 351598643,
            "JobAdName": "HR Operations Intern",
            "LocNames": ["Beijing"],
            "Kind": "Intern",
            "ClassificationOne": "Operations",
            "Duty": "Support HR operations.",
            "Require": "Bachelor degree or above.",
            "DetailUrl": "/job/351598643",
        }
        jobs = parse_beisen_payload({"Data": [concrete]}, SOURCE)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["source_job_id"], "351598643")
        self.assertEqual(jobs[0]["apply_url"], "https://fixture.zhiye.com/job/351598643")

        del concrete["DetailUrl"]
        self.assertEqual(parse_beisen_payload({"Data": [concrete]}, SOURCE), [])


if __name__ == "__main__":
    unittest.main()
