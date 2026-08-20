"""Public 京东 campus recruitment API adapter."""
from __future__ import annotations

import asyncio
import hashlib
import re
import json
import httpx
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from playwright.async_api import async_playwright

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_category, normalize_city, normalize_degree, normalize_job_nature

LIST_PATH = "/api/wx/position/page"
DETAIL_PATH = "/api/wx/position/detail"

def _payload(page_index: int, page_size: int) -> dict[str, Any]:
    return {"pageSize": page_size, "pageIndex": page_index, "parameter": {
        "positionName": "", "planIdList": [], "jobDirectionCodeList": [],
        "workCityCodeList": [], "positionDeptList": [],
    }}

def _detail_url(source: dict[str, Any], job_id: str) -> str:
    p = urlsplit(source["url"])
    return urlunsplit((p.scheme, p.netloc, "/", "", f"/details?id={job_id}"))

def _cities(raw: dict[str, Any]) -> str:
    values: list[str] = []
    for item in raw.get("requirementVoList") or []:
        if not isinstance(item, dict):
            continue
        value = str(item.get("workCity") or "").strip()
        if value and value not in values:
            values.append(value)
    return " / ".join(values)

def _year(text: str) -> str | None:
    m = re.search(r"(20\d{2})\s*年?\s*(?:毕业|届)", text)
    if m:
        return m.group(1)
    m = re.search(r"(?<!\d)(\d{2})\s*届", text)
    return f"20{m.group(1)}" if m else None

def normalize_jd_job(raw: dict[str, Any], source: dict[str, Any]) -> dict[str, Any] | None:
    job_id = str(raw.get("publishId") or "").strip()
    title = str(raw.get("positionName") or "").strip()
    description = str(raw.get("workContent") or "").strip()
    requirements = str(raw.get("qualification") or "").strip()
    if not job_id or not title or not (description or requirements):
        return None
    combined = f"{title} {description} {requirements}"
    nature = normalize_job_nature(str(raw.get("recruitType") or ""), title, combined)
    if nature is None:
        return None
    published = raw.get("publishTime")
    if isinstance(published, (int, float)):
        published = datetime.fromtimestamp(published / 1000, tz=timezone.utc).isoformat()
    canonical = {
        "company": source["company"], "title": title[:160],
        "city": normalize_city(_cities(raw)), "job_nature": nature,
        "category": normalize_category(str(raw.get("jobCategory") or raw.get("jobDirection") or ""), title, combined),
        "degree": normalize_degree(str(raw.get("education") or ""), requirements),
        "graduate_year": _year(combined), "requirements": requirements or None,
        "description": description or None, "apply_url": _detail_url(source, job_id),
        "source_url": source["url"], "source_job_id": job_id,
        "published_at": str(published or "") or None,
    }
    digest = "|".join(str(canonical.get(k) or "") for k in ("company", "title", "city", "job_nature", "source_job_id", "apply_url"))
    canonical["content_hash"] = hashlib.sha256(digest.encode("utf-8")).hexdigest()
    canonical["source_id"] = source["id"]
    canonical["raw"] = raw
    return canonical

class JdAdapter:
    def __init__(self) -> None:
        self._detail_client = httpx.Client(timeout=30.0, headers={"Content-Type": "application/json"})

    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        page_size = min(max(int(source.get("page_size", 20)), 1), 50)
        max_pages = min(max(int(source.get("max_pages", 50)), 1), 50)
        types = source.get("position_types") or ["present", "internship"]
        response_urls: list[str] = []
        records: dict[str, dict[str, Any]] = {}
        complete = True
        stop_reason: str | None = None
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            context = await browser.new_context(locale="zh-CN")
            page = await context.new_page()
            try:
                for position_type in types:
                    first_total: int | None = None
                    page_index = 0
                    while page_index < max_pages:
                        response = await page.request.post(
                            f"{source['url'].rstrip('/')}{LIST_PATH}?type={position_type}",
                            data=_payload(page_index, page_size), timeout=30000,
                        )
                        response_urls.append(response.url)
                        if response.status in {403, 429}:
                            return CollectionResult([], False, response_urls, f"http_{response.status}")
                        if response.status != 200:
                            return CollectionResult([], False, response_urls, f"http_{response.status}")
                        payload = await response.json()
                        body = payload.get("body") if isinstance(payload, dict) else None
                        rows = body.get("items") if isinstance(body, dict) else None
                        total = int(body.get("totalNumber") or 0) if isinstance(body, dict) else -1
                        if not isinstance(rows, list) or total < 0:
                            return CollectionResult([], False, response_urls, "public_job_list_invalid")
                        if first_total is None:
                            first_total = total
                        elif total != first_total:
                            return CollectionResult([], False, response_urls, "jd_source_count_changed")
                        before = len(records)
                        for raw in rows:
                            if isinstance(raw, dict) and raw.get("publishId"):
                                records.setdefault(f"{position_type}:{raw['publishId']}", {**raw, "_jd_type": position_type})
                        if len([k for k in records if k.startswith(position_type + ':')]) >= total:
                            break
                        if not rows or len(rows) < page_size or len(records) == before:
                            return CollectionResult([], False, response_urls, "jd_pagination_ended_before_source_count")
                        page_index += 1
                    else:
                        return CollectionResult([], False, response_urls, "jd_page_limit_before_source_count")
            finally:
                await browser.close()
        items = [ListingItem(str(raw["publishId"]), str(raw.get("positionName") or ""), _detail_url(source, str(raw["publishId"])), raw) for raw in records.values()]
        return CollectionResult(items, complete, response_urls, stop_reason)

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        # The detail contract is a public JSON POST and needs no browser
        # session.  Keep the fan-out sequential while avoiding one browser
        # process per job (the previous implementation made 215 details too
        # slow and was stopped before any database mutation).
        url = f"{source['url'].rstrip('/')}{DETAIL_PATH}/{item.source_job_id}"

        def request_detail() -> dict[str, Any]:
            response = self._detail_client.post(url)
            if response.status_code in {403, 429}:
                raise RuntimeError(f"http_{response.status_code}")
            payload = response.json()
            body = payload.get("body") if isinstance(payload, dict) else None
            if not isinstance(body, dict) or not body.get("publishId"):
                raise RuntimeError("jd_detail_missing")
            return body

        return await asyncio.to_thread(request_detail)

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        return normalize_jd_job(raw, source)

__all__ = ["JdAdapter", "normalize_jd_job"]
