"""MiHoYo public campus ATS adapter.

The campus page exposes a public list endpoint and a public detail endpoint.
The adapter keeps the requests bounded and sequential: at most 20 listings per
run, followed by one detail request per accepted listing when the detail text
is not already present in the list payload.
"""

from __future__ import annotations

import asyncio
import hashlib
from typing import Any

from playwright.async_api import async_playwright

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import (
    normalize_category,
    normalize_city,
    normalize_degree,
    normalize_job_nature,
)


LIST_ENDPOINT = "https://ats.openout.mihoyo.com/ats-portal/v1/job/list"
DETAIL_ENDPOINT = "https://ats.openout.mihoyo.com/ats-portal/v1/job/info"


def _as_text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        parts = [_as_text(item) for item in value]
        return "\n".join(item for item in parts if item)
    if isinstance(value, dict):
        for key in ("text", "content", "value", "name", "label", "addressDetail"):
            text = _as_text(value.get(key))
            if text:
                return text
    return ""


def _first_text(obj: Any, keys: tuple[str, ...]) -> str:
    if not isinstance(obj, dict):
        return ""
    for key in keys:
        value = _as_text(obj.get(key))
        if value:
            return value
    return ""


def _detail_payload(raw: dict[str, Any]) -> dict[str, Any]:
    detail = raw.get("detail")
    if isinstance(detail, dict):
        data = detail.get("data")
        if isinstance(data, dict):
            return data
        return detail
    return {}


def _cities(raw: dict[str, Any]) -> str | None:
    values: list[str] = []
    for item in raw.get("addressDetailList") or raw.get("addressList") or []:
        value = _as_text(item)
        if value and value not in values:
            values.append(value)
    if not values:
        value = _first_text(raw, ("city", "address", "workCity"))
        if value:
            values.append(value)
    return normalize_city(" / ".join(values) if values else None)


def _detail_url(position_id: str) -> str:
    return f"https://jobs.mihoyo.com/#/campus/position/{position_id}"


def _category(raw_category: str, title: str, text: str) -> str:
    """Prefer MiHoYo's explicit competency label over incidental keywords."""
    explicit = {
        "算法类": "算法/AI",
        "开发类": "软件研发",
        "技术类": "软件研发",
        "安全类": "软件研发",
        "测试类": "测试/质量",
        "大数据类": "数据",
        "数据类": "数据",
        "产品类": "产品",
        "运营类": "运营",
        "营销类": "市场/销售",
        "市场类": "市场/销售",
        "职能类": "职能",
        "设计类": "设计",
    }
    if raw_category in explicit:
        return explicit[raw_category]
    # MiHoYo's current API uses broader channel labels for some campus jobs.
    # These labels are authoritative only at the family level; use the title
    # to split the broad technical/international groups, and deliberately do
    # not inspect long requirements text for incidental words such as "AI".
    broad = {
        "综合类": "职能",
        "市场&商务类": "市场/销售",
        "产品策划类": "产品",
        "程序&技术类": None,
        "国际化类": None,
    }
    if raw_category in broad:
        mapped = broad[raw_category]
        if mapped:
            return mapped
        return normalize_category("", title, title)
    return normalize_category(raw_category, title, text)


def normalize_mihoyo_job(raw: dict[str, Any], source: dict[str, Any]) -> dict[str, Any] | None:
    listing = raw.get("listing") if isinstance(raw.get("listing"), dict) else raw
    detail = _detail_payload(raw)
    merged = dict(listing)
    merged.update({key: value for key, value in detail.items() if value not in (None, "", [], {})})

    position_id = str(merged.get("id") or listing.get("id") or "").strip()
    title = _first_text(merged, ("title", "jobTitle", "positionName"))
    if not position_id or not title:
        return None

    responsibilities = _first_text(
        detail,
        ("responsibility", "responsibilities", "jobResponsibility", "jobResponsibilities", "workContent", "duty"),
    )
    description = _first_text(detail, ("jobDescription", "description", "jobSummary")) or _first_text(
        listing, ("jobSummary", "description", "jobDescription")
    )
    requirements = _first_text(
        detail,
        ("requirement", "requirements", "jobRequire", "jobRequirement", "jobRequirements", "qualification", "qualifications", "任职要求"),
    )
    if responsibilities and description and responsibilities not in description:
        description = f"{description}\n{responsibilities}"
    if not description and responsibilities:
        description = responsibilities
    if not (description or requirements):
        return None

    raw_nature = _first_text(merged, ("jobNature", "job_nature", "nature", "hireType", "recruitmentType"))
    nature = normalize_job_nature(raw_nature, title, f"{description} {requirements}")
    if nature is None:
        return None

    category_raw = _first_text(merged, ("competencyType", "jobCategory", "category", "function"))
    degree_raw = _first_text(detail, ("degree", "education", "educationRequirement", "requiredDegree"))
    if not degree_raw:
        degree_raw = _first_text(listing, ("degree", "education", "requiredDegree"))

    canonical = {
        "company": source["company"],
        "title": title[:160],
        "city": _cities(merged),
        "job_nature": nature,
        "category": _category(category_raw, title, f"{description} {requirements}"),
        "degree": normalize_degree(degree_raw, requirements),
        "graduate_year": None,
        "requirements": requirements or None,
        "description": description or None,
        "apply_url": _detail_url(position_id),
        "source_url": source["url"],
        "source_job_id": position_id,
        "published_at": _first_text(merged, ("publishedAt", "publishTime", "updateTime")) or None,
    }
    digest = "|".join(str(canonical.get(key) or "") for key in (
        "company", "title", "city", "job_nature", "source_job_id", "apply_url",
    ))
    canonical["content_hash"] = hashlib.sha256(digest.encode("utf-8", "ignore")).hexdigest()
    canonical["source_id"] = source["id"]
    canonical["raw"] = raw
    return canonical


def _records(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], int]:
    data = payload.get("data")
    candidates = [data, payload]
    for candidate in candidates:
        if isinstance(candidate, list):
            return [item for item in candidate if isinstance(item, dict)], len(candidate)
        if not isinstance(candidate, dict):
            continue
        for key in ("records", "list", "jobList", "positionList", "items"):
            value = candidate.get(key)
            if isinstance(value, list):
                total = candidate.get("total") or candidate.get("totalCount") or len(value)
                return [item for item in value if isinstance(item, dict)], int(total)
    return [], 0


class MihoyoAdapter:
    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        max_jobs = min(max(int(source.get("max_jobs", 20)), 1), 20)
        channel_ids = source.get("channel_detail_ids") or [1]
        hire_type = source.get("hire_type", 1)
        request_payload = {
            "pageNo": 1,
            "pageSize": max_jobs,
            "channelDetailIds": channel_ids,
            "hireType": hire_type,
        }
        response_urls = [LIST_ENDPOINT]
        payload: dict[str, Any] | None = None
        blocked: str | None = None
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context(locale="zh-CN")
            page = await context.new_page()
            try:
                navigation = await page.goto(source["url"], wait_until="domcontentloaded", timeout=30000)
                if navigation and navigation.status in {403, 429}:
                    blocked = f"http_{navigation.status}"
                if not blocked:
                    response = await page.request.post(LIST_ENDPOINT, data=request_payload, timeout=30000)
                    if response.status in {403, 429}:
                        blocked = f"http_{response.status}"
                    elif response.status == 200:
                        candidate = await response.json()
                        if isinstance(candidate, dict):
                            payload = candidate
            finally:
                await browser.close()
        if blocked:
            return CollectionResult([], False, response_urls, blocked)
        if not payload:
            return CollectionResult([], False, response_urls, "public_job_list_missing")
        records, total = _records(payload)
        items: list[ListingItem] = []
        for raw in records[:max_jobs]:
            position_id = str(raw.get("id") or raw.get("jobId") or "").strip()
            title = _first_text(raw, ("title", "jobTitle", "positionName"))
            if position_id and title:
                items.append(ListingItem(position_id, title, _detail_url(position_id), raw))
        return CollectionResult(items, total <= len(items), response_urls)

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        delay_ms = max(int(source.get("job_delay_ms", 1200)), 0)
        if delay_ms:
            await asyncio.sleep(delay_ms / 1000)
        payload = {
            "id": item.source_job_id,
            "channelDetailIds": source.get("channel_detail_ids") or [1],
            "hireType": source.get("hire_type", 1),
        }
        async with async_playwright() as playwright:
            request = await playwright.request.new_context()
            try:
                response = await request.post(DETAIL_ENDPOINT, data=payload, timeout=30000)
                if response.status in {403, 429}:
                    raise RuntimeError(f"http_{response.status}")
                if response.status != 200:
                    return {"listing": item.raw}
                detail = await response.json()
                return {"listing": item.raw, "detail": detail}
            finally:
                await request.dispose()

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        return normalize_mihoyo_job(raw, source)


__all__ = ["MihoyoAdapter", "normalize_mihoyo_job"]
