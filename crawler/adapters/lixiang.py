"""Bounded adapter for Li Auto's public campus recruitment API."""

from __future__ import annotations

import hashlib
import re
from typing import Any

from playwright.async_api import async_playwright

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_job


API_BASE = "https://api-web.lixiang.com/osd-hr-recruitment-website/v1/recruit"


def _text(value: Any) -> str:
    value = str(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


class LixiangCampusAdapter:
    async def _request(self, context: Any, path: str, params: dict[str, Any]) -> dict[str, Any]:
        response = await context.get(
            f"{API_BASE}{path}",
            params=params,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Origin": "https://www.lixiang.com",
                "Referer": "https://www.lixiang.com/employ/campus.html?fromJob=1",
            },
        )
        if response.status in (403, 429):
            raise RuntimeError(f"http_{response.status}")
        if not response.ok:
            raise RuntimeError(f"http_{response.status}")
        payload = await response.json()
        if not isinstance(payload, dict) or payload.get("code") != 0:
            raise RuntimeError("invalid_public_api_payload")
        return payload

    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        limit = min(max(int(source.get("max_jobs", 20)), 1), 20)
        page_size = min(max(int(source.get("page_size", limit)), 1), 50)
        list_url = f"{API_BASE}/school/job-page"
        async with async_playwright() as pw:
            request = await pw.request.new_context(timeout=30000)
            try:
                payload = await self._request(
                    request,
                    "/school/job-page",
                    {"page": 1, "page_size": page_size, "project_id": source.get("project_id", 4)},
                )
            except RuntimeError as exc:
                return CollectionResult([], False, [list_url], str(exc))
            finally:
                await request.dispose()
        data = payload.get("data") or {}
        rows = data.get("items") if isinstance(data, dict) else None
        if not isinstance(rows, list):
            return CollectionResult([], False, [list_url], "no_concrete_public_jobs")
        items = []
        for row in rows[:limit]:
            if not isinstance(row, dict) or not row.get("id") or not row.get("title"):
                continue
            items.append(ListingItem(
                str(row["id"]),
                str(row["title"]),
                f"{source['url'].split('?')[0].rstrip('/')}/../detail/{row['id']}.html?fromJob=1",
                row,
            ))
        if not items:
            return CollectionResult([], False, [list_url], "no_concrete_public_jobs")
        return CollectionResult(items, False, [list_url])

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        async with async_playwright() as pw:
            request = await pw.request.new_context(timeout=30000)
            try:
                payload = await self._request(request, "/job/detail", {"job_id": item.source_job_id})
            finally:
                await request.dispose()
        data = payload.get("data") or {}
        if not isinstance(data, dict):
            return {}
        return {
            **item.raw,
            "source_job_id": str(data.get("id") or item.source_job_id),
            "title": data.get("title") or item.title,
            "city": data.get("location_title"),
            "job_nature": data.get("job_mode_name"),
            "category": data.get("second_job_function_title") or data.get("first_job_function_title"),
            "description": _text(data.get("description")),
            "requirements": _text(data.get("requirements")),
            "degree": data.get("education"),
            "published_at": data.get("published_at"),
        }

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        job = normalize_job(raw, source)
        if not job or not job.get("requirements") or not job.get("description"):
            return None
        job["apply_url"] = f"https://www.lixiang.com/employ/detail/{raw.get('source_job_id')}.html?fromJob=1"
        digest = "|".join(str(job.get(k) or "") for k in (
            "company", "title", "city", "job_nature", "source_job_id", "apply_url",
            "description", "requirements",
        ))
        job["content_hash"] = hashlib.sha256(digest.encode("utf-8", "ignore")).hexdigest()
        return job


__all__ = ["LixiangCampusAdapter"]
