"""Adapter for Papergames' public campus position list API.

The page exposes complete position cards in the public list response, so the
adapter does not fan out into detail-page requests.  This keeps the source
low-frequency and makes the list response itself the auditable evidence.
"""

from __future__ import annotations

import asyncio
import hashlib
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from playwright.async_api import async_playwright

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import (
    normalize_category,
    normalize_city,
    normalize_degree,
    normalize_job_nature,
)


def _name(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, dict):
        for key in ("zh_cn", "name", "i18n_name", "label", "value"):
            if value.get(key):
                return str(value[key]).strip()
    return None


def _cities(raw: dict[str, Any]) -> str | None:
    values: list[str] = []
    for item in raw.get("city_list") or []:
        value = _name(item)
        if value and value not in values:
            values.append(value)
    info = raw.get("job_post_info") or {}
    for item in info.get("address_list") or []:
        city = item.get("city") if isinstance(item, dict) else None
        value = _name(city) or _name(item)
        if value and value not in values:
            values.append(value)
    return normalize_city(" / ".join(values) if values else None)


def _detail_url(source: dict[str, Any], job_id: str) -> str:
    parts = urlsplit(source["url"])
    return urlunsplit((parts.scheme, parts.netloc, "/campus/position/" + job_id + "/detail", "", ""))


def normalize_papegames_job(raw: dict[str, Any], source: dict[str, Any]) -> dict[str, Any] | None:
    job_id = str(raw.get("id") or "").strip()
    title = str(raw.get("title") or "").strip()
    description = str(raw.get("description") or "").strip()
    requirements = str(raw.get("requirement") or "").strip()
    if not job_id or not title or not (description or requirements):
        return None

    recruit_type = raw.get("recruit_type") or {}
    nature_text = " / ".join(filter(None, (_name(recruit_type.get("parent")), _name(recruit_type))))
    category = _name(raw.get("job_category"))
    info = raw.get("job_post_info") or {}
    degree = _name(info.get("required_degree"))
    published = raw.get("publish_time")
    if isinstance(published, (int, float)):
        published = datetime.fromtimestamp(published / 1000, tz=timezone.utc).isoformat()
    elif published is not None:
        published = str(published)

    canonical = {
        "company": source["company"],
        "title": title[:160],
        "city": _cities(raw),
        "job_nature": normalize_job_nature(nature_text, title, description + " " + requirements),
        "category": normalize_category(category, title, description + " " + requirements),
        "degree": normalize_degree(degree, requirements),
        "graduate_year": None,
        "requirements": requirements or None,
        "description": description or None,
        "apply_url": _detail_url(source, job_id),
        "source_url": source["url"],
        "source_job_id": job_id,
        "published_at": published,
    }
    digest = "|".join(str(canonical.get(key) or "") for key in (
        "company", "title", "city", "job_nature", "source_job_id", "apply_url"
    ))
    canonical["content_hash"] = hashlib.sha256(digest.encode("utf-8", "ignore")).hexdigest()
    canonical["source_id"] = source["id"]
    canonical["raw"] = raw
    return canonical


def _list_url(url: str, limit: int) -> str:
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["limit"] = str(min(max(limit, 1), 20))
    query["offset"] = "0"
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), ""))


class PapegamesAdapter:
    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        payload: dict[str, Any] | None = None
        response_urls: list[str] = []
        blocked: str | None = None
        max_jobs = min(max(int(source.get("max_jobs", 20)), 1), 20)
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context(locale="zh-CN")
            page = await context.new_page()

            async def on_response(response):
                nonlocal payload, blocked
                if "/api/v1/search/job/posts" not in response.url:
                    return
                response_urls.append(response.url)
                if response.status in {403, 429}:
                    blocked = f"http_{response.status}"
                    return
                if response.status != 200:
                    return
                try:
                    candidate = await response.json()
                    if isinstance(candidate, dict):
                        payload = candidate
                except Exception:
                    return

            page.on("response", on_response)
            try:
                navigation = await page.goto(_list_url(source["url"], max_jobs), wait_until="domcontentloaded", timeout=30000)
                if navigation and navigation.status in {403, 429}:
                    blocked = f"http_{navigation.status}"
                await page.wait_for_timeout(4500)
            finally:
                await browser.close()
        if blocked:
            return CollectionResult([], False, response_urls, blocked)
        if not payload:
            return CollectionResult([], False, response_urls, "public_job_list_missing")
        data = payload.get("data") or {}
        raw_jobs = data.get("job_post_list") if isinstance(data, dict) else None
        if not isinstance(raw_jobs, list):
            return CollectionResult([], False, response_urls, "public_job_list_invalid")
        items = []
        for raw in raw_jobs[:max_jobs]:
            if not isinstance(raw, dict) or not raw.get("id"):
                continue
            job_id = str(raw["id"])
            items.append(ListingItem(job_id, str(raw.get("title") or ""), _detail_url(source, job_id), raw))
        total = int(data.get("count") or len(items)) if isinstance(data, dict) else len(items)
        return CollectionResult(items, total <= len(items), response_urls)

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        # The list payload already contains description and requirement.  Do
        # not make one request per job detail page.
        return item.raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        return normalize_papegames_job(raw, source)


__all__ = ["PapegamesAdapter", "normalize_papegames_job"]
