"""Bounded adapter for public Beisen/Zhiye 2022 recruitment portals."""

from __future__ import annotations

import hashlib
import json
import re
import asyncio
from typing import Any
from urllib.parse import urlencode, urlsplit, urlunsplit

from playwright.async_api import async_playwright

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_category, normalize_city, normalize_degree, normalize_job_nature


LIST_ENDPOINT_PATH = "/api/Jobad/GetJobAdPageList"
DISPLAY_FIELDS = ["Category", "Kind", "LocId", "ClassificationOne", "WorkWeChatQrCode"]


def _raw_identity(raw: dict[str, Any], page_index: int, row_index: int) -> str:
    job_id = str(raw.get("Id") or "").strip()
    if job_id:
        return job_id
    encoded = json.dumps(raw, ensure_ascii=False, sort_keys=True, default=str)
    digest = hashlib.sha256(encoded.encode("utf-8", "ignore")).hexdigest()[:20]
    # Keep the fallback stable across pages/runs so a repeated page cannot
    # manufacture new observations merely by changing its page index.
    return f"__missing_identity_{digest}"


class BeisenPageAccumulator:
    """Reconcile zero-based Beisen pages against the source-reported Count."""

    def __init__(self, page_size: int):
        self.page_size = page_size
        self.reported_total: int | None = None
        self.records: dict[str, dict[str, Any]] = {}
        self.next_page_index = 0
        self.complete = False
        self.stop_reason: str | None = None

    def add(self, payload: dict[str, Any], page_index: int) -> bool:
        if page_index != self.next_page_index:
            self.stop_reason = "beisen_page_index_out_of_sequence"
            return False
        rows = payload.get("Data")
        try:
            total = int(payload.get("Count"))
        except (TypeError, ValueError):
            self.stop_reason = "beisen_source_count_missing"
            return False
        if payload.get("Code") != 200 or total < 0 or not isinstance(rows, list):
            self.stop_reason = "public_job_list_invalid"
            return False
        if self.reported_total is None:
            self.reported_total = total
        elif total != self.reported_total:
            self.stop_reason = "beisen_source_count_changed"
            return False

        before = len(self.records)
        for row_index, raw in enumerate(rows):
            if isinstance(raw, dict):
                self.records.setdefault(_raw_identity(raw, page_index, row_index), raw)
        added = len(self.records) - before
        self.next_page_index += 1

        if len(self.records) > total:
            self.stop_reason = "beisen_unique_count_exceeds_source_count"
            return False
        if len(self.records) == total:
            self.complete = True
            return False
        if not rows:
            self.stop_reason = "beisen_pagination_ended_before_source_count"
            return False
        if added == 0:
            self.stop_reason = "beisen_repeated_page_detected"
            return False
        if len(rows) < self.page_size:
            self.stop_reason = "beisen_short_page_before_source_count"
            return False
        return True


def _request_payload(page_index: int, page_size: int, source: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "PageIndex": page_index,
        "PageSize": page_size,
        "KeyWords": "",
        "SpecialType": 0,
        "PortalId": "",
        "DisplayFields": DISPLAY_FIELDS,
    }
    categories = (source or {}).get("categories")
    if categories:
        payload["Category"] = list(categories)
    return payload


def _detail_url(raw: dict[str, Any], source: dict[str, Any]) -> str | None:
    job_id = str(raw.get("Id") or "").strip()
    category_id = str(raw.get("CategoryId") or "").strip()
    route = (source.get("detail_routes") or {}).get(category_id)
    if not job_id or not route:
        return None
    parts = urlsplit(source["url"])
    return urlunsplit((parts.scheme, parts.netloc, str(route), urlencode({"jobAdId": job_id}), ""))


def normalize_beisen_job(raw: dict[str, Any], source: dict[str, Any]) -> dict[str, Any] | None:
    job_id = str(raw.get("Id") or "").strip()
    title = str(raw.get("JobAdName") or "").strip()
    description = str(raw.get("Duty") or "").strip()
    requirements = str(raw.get("Require") or "").strip()
    apply_url = _detail_url(raw, source)
    if not job_id or not title or not apply_url or not (description or requirements):
        return None

    cities = raw.get("LocNames") or []
    city_text = " / ".join(str(value).strip() for value in cities if str(value).strip()) if isinstance(cities, list) else str(cities)
    nature = normalize_job_nature(str(raw.get("Kind") or raw.get("Category") or ""), title, description)
    if nature is None:
        return None
    combined = f"{title} {requirements}"
    year = re.search(r"(20\d{2})\s*年?\s*(?:应届|届|春|秋)", combined)
    short_year = re.search(r"(?<!\d)(\d{2})\s*(?:届|春|秋)", combined)
    graduate_year = year.group(1) if year else (f"20{short_year.group(1)}" if short_year else None)
    published = str(raw.get("ChangeDate") or raw.get("PostDate") or "").strip()
    if published.startswith("0001-01-01"):
        published = ""

    canonical = {
        "company": source["company"],
        "title": title[:160],
        "city": normalize_city(city_text),
        "job_nature": nature,
        "category": normalize_category(str(raw.get("ClassificationOne") or ""), title, description),
        "degree": normalize_degree(str(raw.get("Degree") or ""), requirements),
        "graduate_year": graduate_year,
        "requirements": requirements or None,
        "description": description or None,
        "apply_url": apply_url,
        "source_url": source["url"],
        "source_job_id": job_id,
        "published_at": published or None,
    }
    digest = "|".join(str(canonical.get(key) or "") for key in (
        "company", "title", "city", "job_nature", "source_job_id", "apply_url",
    ))
    canonical["content_hash"] = hashlib.sha256(digest.encode("utf-8", "ignore")).hexdigest()
    canonical["source_id"] = source["id"]
    canonical["raw"] = raw
    return canonical


class BeisenAdapter:
    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        first_payload: dict[str, Any] | None = None
        response_urls: list[str] = []
        blocked: str | None = None
        page_size = min(max(int(source.get("page_size", 20)), 1), 50)
        max_pages = min(max(int(source.get("max_pages", 50)), 1), 50)
        page_delay_ms = max(int(source.get("page_delay_ms", 500)), 0)
        parts = urlsplit(source["url"])
        list_endpoint = urlunsplit((parts.scheme, parts.netloc, LIST_ENDPOINT_PATH, "", ""))
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context(locale="zh-CN")
            page = await context.new_page()

            async def on_response(response):
                nonlocal first_payload, blocked
                if LIST_ENDPOINT_PATH not in response.url:
                    return
                response_urls.append(response.url)
                if response.status in {403, 429}:
                    blocked = f"http_{response.status}"
                    return
                if response.status != 200:
                    return
                try:
                    candidate = await response.json()
                    if isinstance(candidate, dict) and first_payload is None:
                        first_payload = candidate
                except Exception:
                    return

            page.on("response", on_response)
            try:
                navigation = await page.goto(source["url"], wait_until="domcontentloaded", timeout=30000)
                if navigation and navigation.status in {403, 429}:
                    blocked = f"http_{navigation.status}"
                await page.wait_for_timeout(5000)
                if blocked:
                    return CollectionResult([], False, response_urls, blocked)
                categories = source.get("categories")
                if categories:
                    # When a category filter is configured, the page's own
                    # default request may only expose one category. Issue a
                    # direct bounded POST for the authoritative first page so
                    # the accumulator reconciles against the category-scoped
                    # total (e.g. campus + internship) rather than the page tab.
                    try:
                        candidate = await page.request.post(
                            list_endpoint,
                            data=_request_payload(0, page_size, source),
                            timeout=30000,
                        )
                        response_urls.append(candidate.url)
                        if candidate.status in {403, 429}:
                            return CollectionResult([], False, response_urls, f"http_{candidate.status}")
                        if candidate.status != 200:
                            return CollectionResult([], False, response_urls, f"http_{candidate.status}")
                        first_payload = await candidate.json()
                    except Exception:
                        return CollectionResult([], False, response_urls, "public_job_page_request_failed")
                if not first_payload:
                    return CollectionResult([], False, response_urls, "public_job_list_missing")

                accumulator = BeisenPageAccumulator(page_size)
                needs_more = accumulator.add(first_payload, 0)
                while needs_more:
                    page_index = accumulator.next_page_index
                    if page_index >= max_pages:
                        accumulator.stop_reason = "beisen_page_limit_before_source_count"
                        break
                    if page_delay_ms:
                        await asyncio.sleep(page_delay_ms / 1000)
                    try:
                        response = await page.request.post(
                            list_endpoint,
                            data=_request_payload(page_index, page_size, source),
                            timeout=30000,
                        )
                    except Exception:
                        accumulator.stop_reason = "public_job_page_request_failed"
                        break
                    response_urls.append(response.url)
                    if response.status in {403, 429}:
                        accumulator.stop_reason = f"http_{response.status}"
                        break
                    if response.status != 200:
                        accumulator.stop_reason = f"http_{response.status}"
                        break
                    try:
                        candidate = await response.json()
                    except Exception:
                        accumulator.stop_reason = "public_job_list_invalid_json"
                        break
                    if not isinstance(candidate, dict):
                        accumulator.stop_reason = "public_job_list_invalid"
                        break
                    needs_more = accumulator.add(candidate, page_index)

                items: list[ListingItem] = []
                for identity, raw in accumulator.records.items():
                    title = str(raw.get("JobAdName") or "").strip()
                    detail_url = _detail_url(raw, source)
                    items.append(ListingItem(identity, title, detail_url or source["url"], raw))
                return CollectionResult(
                    items,
                    accumulator.complete,
                    response_urls,
                    accumulator.stop_reason,
                )
            finally:
                await browser.close()

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        return item.raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        return normalize_beisen_job(raw, source)


__all__ = ["BeisenAdapter", "BeisenPageAccumulator", "normalize_beisen_job"]
