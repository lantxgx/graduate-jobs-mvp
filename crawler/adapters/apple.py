"""Bounded adapter for Apple's public China jobs API.

The source is queried with a graduate/intern keyword and only records whose
official title explicitly contains ``intern`` or ``实习`` are accepted.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

from playwright.async_api import async_playwright

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_job


SEARCH_ENDPOINT = "https://jobs.apple.com/api/v1/search"
DETAIL_ENDPOINT = "https://jobs.apple.com/api/v1/jobDetails/{job_id}"


def _is_internship_title(title: str) -> bool:
    text = title.lower()
    return "intern" in text or "实习" in text


class AppleCampusAdapter:
    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        limit = min(max(int(source.get("max_jobs", 3)), 1), 20)
        body = {
            "query": "China intern",
            "filters": {},
            "page": 1,
            "locale": "zh-cn",
            "sort": "newest",
            "format": {"longDate": "MMMM D, YYYY", "mediumDate": "MMM D, YYYY"},
        }
        async with async_playwright() as pw:
            request = await pw.request.new_context(
                timeout=30000,
                extra_http_headers={
                    "User-Agent": "Mozilla/5.0",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Origin": "https://jobs.apple.com",
                    "Referer": source["url"],
                },
            )
            try:
                response = await request.post(SEARCH_ENDPOINT, data=json.dumps(body))
                if response.status in (403, 429):
                    return CollectionResult([], False, [SEARCH_ENDPOINT], f"http_{response.status}")
                if not response.ok:
                    return CollectionResult([], False, [SEARCH_ENDPOINT], f"http_{response.status}")
                payload = await response.json()
            except Exception as exc:
                return CollectionResult([], False, [SEARCH_ENDPOINT], f"request_error:{type(exc).__name__}")
            finally:
                await request.dispose()

        rows = ((payload.get("res") or {}).get("searchResults") if isinstance(payload, dict) else None) or []
        items: list[ListingItem] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            title = str(row.get("postingTitle") or "").strip()
            job_id = str(row.get("id") or row.get("jobPositionId") or "").strip()
            if not job_id or not title or not _is_internship_title(title):
                continue
            items.append(
                ListingItem(
                    job_id,
                    title,
                    f"https://jobs.apple.com/zh-cn/details/{row.get('positionId') or job_id}",
                    row,
                )
            )
            if len(items) >= limit:
                break
        if not items:
            return CollectionResult([], False, [SEARCH_ENDPOINT], "no_qualified_internship_jobs")
        return CollectionResult(items, False, [SEARCH_ENDPOINT])

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        async with async_playwright() as pw:
            request = await pw.request.new_context(
                timeout=30000,
                extra_http_headers={
                    "User-Agent": "Mozilla/5.0",
                    "Accept": "application/json",
                    "Origin": "https://jobs.apple.com",
                    "Referer": source["url"],
                },
            )
            try:
                response = await request.get(DETAIL_ENDPOINT.format(job_id=item.source_job_id))
                if not response.ok:
                    return {}
                payload = await response.json()
            finally:
                await request.dispose()
        detail = (payload.get("res") if isinstance(payload, dict) else None) or {}
        if not isinstance(detail, dict):
            return {}
        requirements = "\n\n".join(
            value.strip()
            for value in (
                str(detail.get("minimumQualifications") or ""),
                str(detail.get("preferredQualifications") or ""),
            )
            if value.strip()
        )
        position_id = detail.get("positionId") or item.raw.get("positionId") or item.source_job_id
        return {
            "id": str(detail.get("id") or item.source_job_id),
            "title": detail.get("postingTitle") or item.title,
            "job_type": "实习",
            "category": (detail.get("teamNames") or ["其他"])[0],
            "description": detail.get("description") or detail.get("jobSummary"),
            "requirements": requirements,
            "workplace": "",
            "apply_url": f"https://jobs.apple.com/zh-cn/details/{position_id}",
            "published_at": detail.get("postDateInGMT") or detail.get("postingDateMeta"),
        }

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        title = str(raw.get("title") or "").strip()
        if not _is_internship_title(title):
            return None
        job = normalize_job(raw, source)
        if not job or not job.get("description") or not job.get("requirements"):
            return None
        digest = "|".join(
            str(job.get(key) or "")
            for key in ("company", "title", "city", "job_nature", "source_job_id", "apply_url", "description", "requirements")
        )
        job["content_hash"] = hashlib.sha256(digest.encode("utf-8", "ignore")).hexdigest()
        return job


__all__ = ["AppleCampusAdapter"]
