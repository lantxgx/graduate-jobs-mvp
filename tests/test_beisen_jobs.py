import json
from pathlib import Path
import asyncio
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app import db
from crawler.adapters.base import CollectionResult, ListingItem
from crawler.adapters.beisen import BeisenPageAccumulator, _request_payload, normalize_beisen_job
from crawler.runner import crawl_source
from crawler.beisen_jobs import parse_beisen_payload
from crawler.browser_discovery import blocked_signal
from crawler.runner import is_qualified_job


SOURCE = {
    "id": "beisen-fixture",
    "company": "Fixture Company",
    "url": "https://fixture.zhiye.com/campus/jobs",
    "campus_only": True,
}

LIVE_SHAPE_SOURCE = {
    "id": "360-campus",
    "company": "360",
    "url": "https://360campus.zhiye.com/jobs",
    "campus_only": True,
    "detail_routes": {"2": "/campus/detail", "3": "/intern/detail", "5": "/5/detail"},
}


class BeisenAdapterTests(unittest.TestCase):
    def test_zero_based_pages_terminate_at_reported_count(self):
        pages = json.loads((Path(__file__).parent / "fixtures" / "beisen_360_pages.json").read_text(encoding="utf-8"))
        accumulator = BeisenPageAccumulator(page_size=2)
        self.assertTrue(accumulator.add(pages[0], 0))
        self.assertEqual(accumulator.next_page_index, 1)
        self.assertFalse(accumulator.add(pages[1], 1))
        self.assertTrue(accumulator.complete)
        self.assertIsNone(accumulator.stop_reason)
        self.assertEqual(accumulator.reported_total, 3)
        self.assertEqual(len(accumulator.records), 3)

    def test_repeated_page_cannot_claim_complete_snapshot(self):
        pages = json.loads((Path(__file__).parent / "fixtures" / "beisen_360_pages.json").read_text(encoding="utf-8"))
        accumulator = BeisenPageAccumulator(page_size=2)
        self.assertTrue(accumulator.add(pages[0], 0))
        self.assertFalse(accumulator.add(pages[0], 1))
        self.assertFalse(accumulator.complete)
        self.assertEqual(accumulator.stop_reason, "beisen_repeated_page_detected")

    def test_repeated_missing_identity_row_uses_stable_fallback(self):
        page = {"Code": 200, "Count": 2, "Data": [{"JobAdName": "Missing identity"}]}
        accumulator = BeisenPageAccumulator(page_size=1)
        self.assertTrue(accumulator.add(page, 0))
        self.assertFalse(accumulator.add(page, 1))
        self.assertEqual(accumulator.stop_reason, "beisen_repeated_page_detected")

    def test_early_empty_page_fails_count_reconciliation(self):
        pages = json.loads((Path(__file__).parent / "fixtures" / "beisen_360_pages.json").read_text(encoding="utf-8"))
        accumulator = BeisenPageAccumulator(page_size=2)
        self.assertTrue(accumulator.add(pages[0], 0))
        self.assertFalse(accumulator.add({"Code": 200, "Count": 3, "Data": []}, 1))
        self.assertFalse(accumulator.complete)
        self.assertEqual(accumulator.stop_reason, "beisen_pagination_ended_before_source_count")

    def test_partial_pagination_failure_does_not_deactivate_existing_jobs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            previous_db_path = db.DB_PATH
            db.DB_PATH = Path(temp_dir) / "jobs.db"
            try:
                db.init_db()
                db.upsert_job({
                    "source_id": "360-campus", "source_job_id": "existing", "company": "360",
                    "title": "Existing Graduate Job", "city": "北京市", "job_nature": "全职",
                    "category": "软件研发", "degree": "本科及以上", "description": "Build services.",
                    "requirements": "Bachelor degree.", "source_url": LIVE_SHAPE_SOURCE["url"],
                    "apply_url": LIVE_SHAPE_SOURCE["url"] + "/existing", "content_hash": "existing-v1", "raw": {},
                })
                adapter = SimpleNamespace(
                    fetch_listing=AsyncMock(return_value=CollectionResult(
                        [ListingItem("partial", "Partial", LIVE_SHAPE_SOURCE["url"], {})],
                        False,
                        ["https://360campus.zhiye.com/api/Jobad/GetJobAdPageList"],
                        "beisen_repeated_page_detected",
                    ))
                )
                registry = SimpleNamespace(get=lambda _name: adapter)
                source = dict(LIVE_SHAPE_SOURCE, adapter="beisen", snapshot_complete=True)
                with patch("crawler.runner.default_registry", return_value=registry), patch.dict(
                    os.environ, {"CRAWL_MIN_INTERVAL_SECONDS": "0"}
                ):
                    result = asyncio.run(crawl_source(source))
                self.assertEqual(result["error"], "beisen_repeated_page_detected")
                with db.connect() as conn:
                    row = conn.execute(
                        "SELECT status, missing_snapshot_count FROM jobs WHERE source_id='360-campus'"
                    ).fetchone()
                self.assertEqual(tuple(row), ("active", 0))
            finally:
                db.DB_PATH = previous_db_path

    def test_normalizes_observed_360_beisen_shape_and_explicit_routes(self):
        payload = json.loads((Path(__file__).parent / "fixtures" / "beisen_360_listing.json").read_text(encoding="utf-8"))
        internship = normalize_beisen_job(payload["Data"][0], LIVE_SHAPE_SOURCE)
        graduate = normalize_beisen_job(payload["Data"][1], LIVE_SHAPE_SOURCE)
        self.assertEqual(internship["source_job_id"], "11111111-1111-4111-8111-111111111111")
        self.assertEqual(internship["job_nature"], "实习")
        self.assertEqual(internship["degree"], "本科及以上")
        self.assertEqual(internship["apply_url"], "https://360campus.zhiye.com/intern/detail?jobAdId=11111111-1111-4111-8111-111111111111")
        self.assertEqual(graduate["job_nature"], "全职")
        self.assertEqual(graduate["graduate_year"], "2026")
        self.assertEqual(graduate["apply_url"], "https://360campus.zhiye.com/campus/detail?jobAdId=22222222-2222-4222-8222-222222222222")
        daily_intern = normalize_beisen_job(payload["Data"][2], LIVE_SHAPE_SOURCE)
        self.assertEqual(daily_intern["job_nature"], "实习")
        self.assertEqual(daily_intern["apply_url"], "https://360campus.zhiye.com/5/detail?jobAdId=33333333-3333-4333-8333-333333333333")

    def test_unknown_beisen_detail_route_is_rejected(self):
        payload = json.loads((Path(__file__).parent / "fixtures" / "beisen_360_listing.json").read_text(encoding="utf-8"))
        self.assertIsNone(normalize_beisen_job(payload["Data"][3], LIVE_SHAPE_SOURCE))

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

    def test_request_payload_includes_category_filter_when_configured(self):
        payload = _request_payload(0, 20, {"categories": ["2", "3"]})
        self.assertEqual(payload["Category"], ["2", "3"])
        no_categories = _request_payload(0, 20, {})
        self.assertNotIn("Category", no_categories)
        legacy = _request_payload(0, 20)
        self.assertNotIn("Category", legacy)

    def test_category_scoped_fixture_normalizes_campus_and_intern(self):
        fixture = json.loads(
            (Path(__file__).parent / "fixtures" / "beisen_beisen_categories_listing.json").read_text(encoding="utf-8")
        )
        source = {
            "id": "beisen-campus-fixture",
            "company": "北森",
            "url": "https://beisen.zhiye.com/campus/jobs",
            "campus_only": True,
            "detail_routes": {"2": "/campus/detail", "3": "/intern/detail"},
            "categories": ["2", "3"],
        }
        accepted = []
        for raw in fixture["Data"]:
            job = normalize_beisen_job(raw, source)
            if job:
                accepted.append(job)
        self.assertEqual(len(accepted), 3)
        by_id = {j["source_job_id"]: j for j in accepted}
        self.assertEqual(by_id["campus-0001-0000-0000-000000000001"]["job_nature"], "全职")
        self.assertEqual(
            by_id["campus-0001-0000-0000-000000000001"]["apply_url"],
            "https://beisen.zhiye.com/campus/detail?jobAdId=campus-0001-0000-0000-000000000001",
        )
        self.assertEqual(by_id["campus-0002-0000-0000-000000000002"]["job_nature"], "实习")
        self.assertEqual(by_id["intern-0003-0000-0000-000000000003"]["job_nature"], "实习")
        self.assertEqual(
            by_id["intern-0003-0000-0000-000000000003"]["apply_url"],
            "https://beisen.zhiye.com/intern/detail?jobAdId=intern-0003-0000-0000-000000000003",
        )

    def test_out_of_scope_category_and_other_kind_are_rejected(self):
        source = {
            "id": "beisen-campus-fixture",
            "company": "北森",
            "url": "https://beisen.zhiye.com/campus/jobs",
            "campus_only": True,
            "detail_routes": {"2": "/campus/detail", "3": "/intern/detail"},
            "categories": ["2", "3"],
        }
        social = {
            "Id": "social-0001", "JobAdName": "销售总监", "CategoryId": "1",
            "Category": "社会招聘", "LocNames": ["北京市"], "Kind": "全职",
            "Duty": "负责销售团队管理。", "Require": "5年以上To B经验。",
        }
        self.assertIsNone(normalize_beisen_job(social, source))

    def test_other_kind_with_campus_intern_evidence_normalizes_to_internship(self):
        source = {
            "id": "beisen-campus-fixture",
            "company": "北森",
            "url": "https://beisen.zhiye.com/campus/jobs",
            "campus_only": True,
            "detail_routes": {"2": "/campus/detail", "3": "/intern/detail"},
            "categories": ["2", "3"],
        }
        other_kind = {
            "Id": "other-0001", "JobAdName": "2027届校招-测试实习生", "CategoryId": "2",
            "Category": "校园招聘", "LocNames": ["大连市"], "Kind": "其他",
            "Duty": "参与测试。", "Require": "本科及以上。",
        }
        job = normalize_beisen_job(other_kind, source)
        self.assertIsNotNone(job)
        self.assertEqual(job["job_nature"], "实习")


if __name__ == "__main__":
    unittest.main()
