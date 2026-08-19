from __future__ import annotations

from typing import Any

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.beisen_jobs import parse_beisen_payload
from crawler.feishu_jobs import discover_feishu_jobs
from crawler.normalize import normalize_job
from crawler.xiaomi_jobs import discover_xiaomi_jobs
from crawler.browser_discovery import discover_job_json


class LegacyModeAdapter:
    """Bridge current source modes into the new adapter contract."""

    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        mode = source.get("mode")
        if mode == "browser_json" or mode == "beisen_jobs_browser":
            raw_jobs, response_urls = await discover_job_json(source["url"])
        elif mode == "xiaomi_jobs_browser":
            raw_jobs, response_urls = await discover_xiaomi_jobs(
                source["url"], max_pages=source.get("max_pages"), page_delay_ms=source.get("page_delay_ms")
            )
        elif mode == "feishu_jobs_browser":
            raw_jobs, response_urls = await discover_feishu_jobs(
                source["url"], max_jobs=source.get("max_jobs"), job_delay_ms=source.get("job_delay_ms")
            )
        else:
            raise ValueError(f"unsupported_source_mode:{mode}")
        items = []
        for index, raw in enumerate(raw_jobs):
            source_job_id = str(raw.get("id") or raw.get("jobId") or raw.get("positionId") or index)
            title = str(raw.get("title") or raw.get("jobName") or "")
            items.append(ListingItem(source_job_id, title, str(raw.get("url") or source["url"]), raw))
        return CollectionResult(items, bool(source.get("snapshot_complete")), response_urls)

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        return item.raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        if source.get("mode") == "beisen_jobs_browser":
            jobs = parse_beisen_payload(raw, source)
            return jobs[0] if jobs else None
        return normalize_job(raw, source)
