"""Adapter for Shanghai AI Laboratory's public campus recruitment API."""

from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

import httpx

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_job


def _zh(value: Any) -> str:
    if isinstance(value, dict):
        if isinstance(value.get("name"), dict):
            value = value["name"]
        return str(value.get("zh_cn") or value.get("en_us") or "").strip()
    return str(value or "").strip()


def _item_to_raw(item: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    address = item.get("address") or {}
    job_id = str(item.get("id") or item.get("job_id") or "").strip()
    detail_url = urljoin(source["url"], f"/joinus/detail/{job_id}?mode=campus")
    return {
        "id": job_id,
        "title": str(item.get("title") or "").strip(),
        "city": _zh(address.get("city")),
        "job_type": _zh(item.get("job_recruitment_type")),
        "category": _zh(item.get("job_function")) or _zh(item.get("job_type")),
        "description": str(item.get("description") or "").strip(),
        "requirements": str(item.get("requirement") or "").strip(),
        "detail_url": detail_url,
        "published_at": item.get("updatedAtShow") or item.get("modify_time"),
    }


class ShlabCampusAdapter:
    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        base = str(source.get("api_base") or "https://www.shlab.org.cn")
        endpoint = urljoin(base, "/api/getJobList")
        max_jobs = min(max(int(source.get("max_jobs", 10)), 1), 20)
        page_size = min(max(int(source.get("page_size", 7)), 1), 20)
        params: dict[str, Any] = {"mode": "campus", "limit": page_size}
        items: list[ListingItem] = []
        response_urls: list[str] = []
        async with httpx.AsyncClient(timeout=30, headers={"Referer": source["url"]}) as client:
            while len(items) < max_jobs:
                response = await client.get(endpoint, params=params)
                response_urls.append(str(response.url))
                if response.status_code in (403, 429):
                    return CollectionResult([], False, response_urls, f"http_{response.status_code}")
                response.raise_for_status()
                payload = response.json()
                data = payload.get("data") if isinstance(payload, dict) else None
                rows = data.get("items") if isinstance(data, dict) else None
                if not isinstance(rows, list) or not rows:
                    break
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    raw = _item_to_raw(row, source)
                    if raw["id"] and raw["title"]:
                        items.append(ListingItem(raw["id"], raw["title"], raw["detail_url"], raw))
                    if len(items) >= max_jobs:
                        break
                if len(items) >= max_jobs or not data.get("has_more"):
                    break
                token = str(data.get("page_token") or "").strip()
                if not token:
                    break
                params["page_token"] = token
        if not items:
            return CollectionResult([], False, response_urls, "no_concrete_public_campus_jobs")
        return CollectionResult(items, False, response_urls)

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        return item.raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        job = normalize_job(raw, source)
        if not job or not job.get("requirements") or not job.get("description"):
            return None
        return job


__all__ = ["ShlabCampusAdapter"]
