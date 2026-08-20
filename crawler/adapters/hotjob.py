"""Adapter for public DaYi/Hotjob campus portals.

The adapter uses only the JSON endpoints called by the public page.  It keeps
the initial snapshot bounded and fetches each selected public detail record so
that descriptions and requirements are evidence-backed.
"""
from __future__ import annotations

import hashlib
from typing import Any
from urllib.parse import urlsplit, urlencode

import httpx

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import (
    normalize_category,
    normalize_degree,
    normalize_job,
    normalize_job_nature,
    normalize_location_name,
)


class HotjobCampusAdapter:
    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        parts = urlsplit(source["url"])
        base = f"{parts.scheme}://{parts.netloc}"
        suite = str(source["suite_key"])
        endpoint = f"{base}/wecruit/positionInfo/listPosition/{suite}"
        max_jobs = min(max(int(source.get("max_jobs", 20)), 1), 50)
        page_size = min(max(int(source.get("page_size", 12)), 1), 30)
        headers = {"User-Agent": "Mozilla/5.0", "Referer": source["url"]}
        items: list[ListingItem] = []
        response_urls: list[str] = []
        async with httpx.AsyncClient(timeout=30, headers=headers) as client:
            page = 1
            while len(items) < max_jobs:
                data = {
                    "isFrompb": "true",
                    "recruitType": int(source.get("recruit_type", 1)),
                    "pageSize": page_size,
                    "currentPage": page,
                }
                if source.get("project_code"):
                    data["projectCode"] = str(source["project_code"])
                response = await client.post(endpoint, params={"iSaJAx": "isAjax", "request_locale": "zh_CN"}, data=data)
                response_urls.append(str(response.url))
                if response.status_code in (403, 429):
                    return CollectionResult([], False, response_urls, f"http_{response.status_code}")
                response.raise_for_status()
                payload = response.json()
                rows = (((payload or {}).get("data") or {}).get("pageForm") or {}).get("pageData") or []
                if not rows:
                    break
                for row in rows:
                    post_id = str(row.get("postId") or "").strip()
                    title = str(row.get("postName") or "").strip()
                    if not post_id or not title:
                        continue
                    detail_url = self._detail_url(source, post_id)
                    items.append(ListingItem(post_id, title, detail_url, row))
                    if len(items) >= max_jobs:
                        break
                total_page = int((((payload or {}).get("data") or {}).get("pageForm") or {}).get("totalPage") or page)
                if page >= total_page:
                    break
                page += 1
        if not items:
            return CollectionResult([], False, response_urls, "no_concrete_visible_job_cards")
        return CollectionResult(items, False, response_urls)

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        parts = urlsplit(source["url"])
        base = f"{parts.scheme}://{parts.netloc}"
        suite = str(source["suite_key"])
        endpoint = f"{base}/wecruit/positionInfo/listPositionDetail/{suite}"
        async with httpx.AsyncClient(timeout=30, headers={"User-Agent": "Mozilla/5.0", "Referer": item.detail_url}) as client:
            response = await client.post(endpoint, params={"iSaJAx": "isAjax", "request_locale": "zh_CN"}, data={"postId": item.source_job_id})
            if response.status_code in (403, 429):
                return {"_error": f"http_{response.status_code}", "listing": item.raw}
            response.raise_for_status()
            payload = response.json()
        detail = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(detail, dict):
            return {"_error": "detail_unavailable", "listing": item.raw}
        return {"detail": detail, "listing": item.raw}

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        if raw.get("_error"):
            return None
        detail = raw.get("detail") or {}
        listing = raw.get("listing") or {}
        title = str(detail.get("postName") or listing.get("postName") or "").strip()
        description = detail.get("workContent") or ""
        requirements = detail.get("serviceCondition") or ""
        if not title or not (description or requirements):
            return None
        cities = []
        for loc in detail.get("workPlaceList") or []:
            name = normalize_location_name(str((loc or {}).get("name") or ""))
            if name and name not in cities:
                cities.append(name)
        city = " / ".join(cities) or normalize_location_name(str(detail.get("workPlaceStr") or listing.get("workPlaceStr") or ""))
        nature = normalize_job_nature(str(detail.get("recruitmentType") or "校园招聘"), title, f"{description} {requirements}")
        if not nature:
            return None
        item = {
            "company": source["company"],
            "title": title,
            "city": city,
            "job_nature": nature,
            "category": normalize_category(detail.get("postTypeName") or listing.get("postTypeName"), title, f"{description} {requirements}"),
            "degree": normalize_degree(None, str(requirements)),
            "graduate_year": None,
            "requirements": requirements,
            "description": description,
            "apply_url": self._detail_url(source, str(detail.get("postId") or listing.get("postId"))),
            "source_url": source["url"],
            "source_job_id": str(detail.get("postId") or listing.get("postId") or ""),
            "published_at": detail.get("publishDate") or listing.get("publishDate"),
        }
        digest = "|".join(str(item.get(k) or "") for k in ("company", "title", "city", "job_nature", "source_job_id", "apply_url", "description", "requirements"))
        item["content_hash"] = hashlib.sha256(digest.encode("utf-8", "ignore")).hexdigest()
        item["source_id"] = source["id"]
        item["raw"] = raw
        return normalize_job(item, source)

    @staticmethod
    def _detail_url(source: dict[str, Any], post_id: str) -> str:
        parts = urlsplit(source["url"])
        query = {"projectCode": source.get("project_code", ""), "postId": post_id}
        return f"{parts.scheme}://{parts.netloc}{parts.path}?{urlencode({k: v for k, v in query.items() if v})}"


__all__ = ["HotjobCampusAdapter"]
