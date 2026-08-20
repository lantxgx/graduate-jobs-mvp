import json
from pathlib import Path
import unittest

from crawler.adapters.pdd import normalize_pdd_job

SOURCE = {
    "id": "pdd-campus",
    "company": "拼多多",
    "url": "https://careers.pddglobalhr.com/campus/grad",
    "campus_only": True,
}


def _load_fixture():
    return json.loads(
        (Path(__file__).parent / "fixtures" / "pdd_listing.json").read_text(encoding="utf-8")
    )


class PddAdapterTests(unittest.TestCase):
    def test_normalizes_concrete_pdd_list_item(self):
        fixture = _load_fixture()
        raw = fixture["result"]["list"][0]
        job = normalize_pdd_job(raw, SOURCE)
        self.assertIsNotNone(job)
        self.assertEqual(job["company"], "拼多多")
        self.assertEqual(job["title"], "区域业务管培生（上海）")
        self.assertEqual(job["city"], "上海")
        self.assertEqual(job["job_nature"], "全职")
        self.assertEqual(job["source_job_id"], "f1a1e001-0000-4000-8000-000000000001")
        self.assertEqual(job["graduate_year"], "2027")
        # no per-job apply URL -> campus list page is the apply entry
        self.assertEqual(job["apply_url"], SOURCE["url"])

    def test_detail_requirement_merges_into_normalization(self):
        fixture = _load_fixture()
        raw = dict(fixture["result"]["list"][0])
        raw["serveRequirement"] = "1、2027届应届本科及以上学历；\n2、具备数据分析能力。"
        job = normalize_pdd_job(raw, SOURCE)
        self.assertIsNotNone(job)
        self.assertIn("2027届应届本科及以上学历", job["requirements"])
        self.assertEqual(job["description"], raw["jobDuty"])

    def test_rejects_row_without_id_or_title(self):
        self.assertIsNone(normalize_pdd_job({}, SOURCE))
        self.assertIsNone(normalize_pdd_job({"id": "x"}, SOURCE))
        self.assertIsNone(normalize_pdd_job({"name": "no id"}, SOURCE))


if __name__ == "__main__":
    unittest.main()
