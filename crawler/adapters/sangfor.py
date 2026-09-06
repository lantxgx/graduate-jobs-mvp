"""Browser-backed adapter for 深信服's public campus job portal."""

from __future__ import annotations

import asyncio
import hashlib
import os
import re
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_category, normalize_city, normalize_degree, normalize_job_nature


REQUIREMENT_MARKERS = ("任职要求", "岗位要求", "职位要求", "岗位需求", "任职资格")


def _text(value: Any) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", BeautifulSoup(str(value), "html.parser").get_text(" ", strip=True)).strip()


def _split_description(value: Any) -> tuple[str, str]:
    text = _text(value)
    marker = next((item for item in REQUIREMENT_MARKERS if item in text), None)
    if not marker:
        return text, ""
    description, requirements = text.split(marker, 1)
    return description.strip(), requirements.strip()


def normalize_sangfor_job(raw: dict[str, Any], source: dict[str, Any]) -> dict[str, Any] | None:
    job_id = str(raw.get("positionId") or "").strip()
    title = str(raw.get("title") or "").strip()
    description, requirements = _split_description(raw.get("description"))
    if not job_id or not title or not description or not requirements:
        return None
    city_raw = str(raw.get("workPlaceText") or "").strip()
    if not city_raw:
        city_match = re.search(r"工作地点\s*[:：]\s*([^，。；<]+)", _text(raw.get("description")))
        city_raw = city_match.group(1).strip() if city_match else ""
    city = normalize_city(city_raw or None)
    if not city:
        return None
    nature = normalize_job_nature(str(raw.get("commitment") or ""), title, description + " " + requirements)
    if nature is None:
        return None
    apply_url = urljoin(source["url"], f"/campucompon/Delivery/{job_id}")
    canonical = {
        "company": source["company"],
        "title": title[:160],
        "city": city,
        "job_nature": nature,
        "category": normalize_category(str(raw.get("functionName") or ""), title, description),
        "degree": normalize_degree(str(raw.get("education") or ""), requirements),
        "graduate_year": None,
        "requirements": requirements,
        "description": description,
        "apply_url": apply_url,
        "source_url": source["url"],
        "source_job_id": job_id,
        "published_at": str(raw.get("openedAt") or "").strip() or None,
    }
    digest = "|".join(str(canonical.get(key) or "") for key in (
        "company", "title", "city", "job_nature", "source_job_id", "apply_url",
    ))
    canonical["content_hash"] = hashlib.sha256(digest.encode("utf-8", "ignore")).hexdigest()
    canonical["source_id"] = source["id"]
    canonical["raw"] = raw
    return canonical


class SangforCampusAdapter:
    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        page_size = min(max(int(source.get("page_size", 10)), 1), 40)
        max_pages = min(max(int(source.get("max_pages", 10)), 1), 20)
        channel_id = int(source.get("channel_id", 101))
        response_urls: list[str] = []
        payload: dict[str, Any] | None = None
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context(locale="zh-CN")
            page = await context.new_page()

            async def capture(response):
                nonlocal payload
                if response.url.endswith("/api/api/Jobs"):
                    response_urls.append(response.url)
                    if response.status == 200:
                        try:
                            candidate = await response.json()
                            if isinstance(candidate, dict) and payload is None:
                                payload = candidate
                        except Exception:
                            pass

            page.on("response", capture)
            try:
                await page.goto(source["url"], wait_until="domcontentloaded", timeout=int(os.getenv("CRAWL_TIMEOUT_MS", "60000")))
                await page.wait_for_timeout(5000)
                if not payload:
                    return CollectionResult([], False, response_urls, "public_job_list_missing")
                data = payload.get("data") or {}
                total = int(data.get("count") or 0)
                rows = list(data.get("listData") or [])
                for page_number in range(2, max_pages + 1):
                    if len(rows) >= total:
                        break
                    request_payload = {
                        "channelId": channel_id, "page": page_number, "pageSize": page_size,
                        "departmentId": 0, "functionId": 0, "kw": "", "locationId": 0, "workPlaceId": 0,
                    }
                    result = await page.evaluate(
                        """async ({url, payload}) => {
                            const response = await fetch(url, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
                            return {status: response.status, body: await response.json()};
                        }""",
                        {"url": urljoin(source["url"], "/api/api/Jobs"), "payload": request_payload},
                    )
                    response_urls.append(urljoin(source["url"], "/api/api/Jobs"))
                    if result.get("status") != 200:
                        return CollectionResult([], False, response_urls, f"http_{result.get('status')}")
                    page_data = (result.get("body") or {}).get("data") or {}
                    page_rows = list(page_data.get("listData") or [])
                    if not page_rows:
                        return CollectionResult([], False, response_urls, "sangfor_pagination_ended_before_count")
                    rows.extend(page_rows)
                unique: dict[str, dict[str, Any]] = {}
                for row in rows:
                    if not isinstance(row, dict) or str(row.get("positionState") or "").lower() not in {"", "open"}:
                        continue
                    if channel_id not in (row.get("channelIds") or [channel_id]):
                        continue
                    job_id = str(row.get("positionId") or "").strip()
                    if job_id:
                        unique.setdefault(job_id, row)
                items = [ListingItem(job_id, str(row.get("title") or ""), urljoin(source["url"], f"/campucompon/Delivery/{job_id}"), row) for job_id, row in unique.items()]
                return CollectionResult(items, len(rows) >= total > 0, response_urls, None if len(rows) >= total else "sangfor_page_limit_before_source_count")
            finally:
                await browser.close()

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        return item.raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        return normalize_sangfor_job(raw, source)


__all__ = ["SangforCampusAdapter", "normalize_sangfor_job"]
