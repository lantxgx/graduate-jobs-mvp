"""Bounded adapter for the public Bilibili campus-position API."""

from __future__ import annotations

import hashlib
import html
import re
from typing import Any

from playwright.async_api import async_playwright

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_job


API_HEADERS = {
    "X-UserType": "2",
    "X-AppKey": "ops.ehr-api.auth",
    "X-Channel": "campus",
}


def _plain(value: Any) -> str:
    text = html.unescape(str(value or ""))
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _split_description(value: Any) -> tuple[str, str]:
    """Split the official combined description without inventing text."""
    text = _plain(value)
    text = re.sub(r"^工作职责\s*[:：]?\s*", "", text)
    match = re.search(r"工作要求\s*[:：]?", text)
    if not match:
        return text, ""
    return text[: match.start()].strip(), text[match.end() :].strip()


def _graduate_year(text: str) -> str | None:
    match = re.search(r"(20\d{2})\s*届", text)
    if match:
        return match.group(1)
    match = re.search(r"(20\d{2})\s+graduate\b", text, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r"class\s+of\s+(20\d{2}(?:\s*/\s*20\d{2})?)", text, re.IGNORECASE)
    return re.sub(r"\s+", "", match.group(1)) if match else None


def normalize_bilibili_position(raw: dict[str, Any], source: dict[str, Any]) -> dict[str, Any] | None:
    job_id = str(raw.get("id") or raw.get("source_job_id") or "").strip()
    title = _plain(raw.get("positionName") or raw.get("title"))
    city = _plain(raw.get("workLocation") or raw.get("location"))
    nature = _plain(raw.get("positionTypeName") or raw.get("job_type"))
    description, requirements = _split_description(raw.get("positionDescription") or raw.get("description"))
    if not all((job_id, title, city, nature, description)):
        return None
    detail_url = f"https://jobs.bilibili.com/campus/positions/{job_id}?type=3"
    canonical_raw = {
        "id": job_id,
        "title": title,
        "city": city,
        "job_type": nature,
        "category": _plain(raw.get("postCodeName")),
        "description": description,
        "requirements": requirements,
        "published_at": raw.get("pushTime"),
        "detail_url": detail_url,
        "graduation_start": raw.get("graduationStartTime"),
        "graduation_end": raw.get("graduationEndTime"),
    }
    job = normalize_job(canonical_raw, source)
    if not job:
        return None
    # normalize_job deliberately owns category, degree and cohort inference;
    # only evidence-backed fields specific to this API are added here.
    job["raw"] = {**raw, "detail_url": detail_url}
    job["graduate_year"] = _graduate_year(f"{title} {description} {requirements}")
    return job


class BilibiliCampusAdapter:
    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        limit = min(max(int(source.get("max_jobs", 20)), 1), 20)
        response_urls = [source["url"], source["url"].split("/campus/")[0] + "/api/campus/position/positionList"]
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                response = await page.goto(
                    source["url"],
                    wait_until="domcontentloaded",
                    timeout=int(source.get("timeout_ms", 30000)),
                )
                if response and response.status in {403, 429}:
                    return CollectionResult([], False, response_urls, f"http_{response.status}")
                payload = await page.evaluate(
                    """async ({pageSize, headers}) => {
                        const csrf = await (await fetch('/api/auth/v1/csrf/token', {headers})).json();
                        if (!csrf || !csrf.data) return {error: 'csrf_token_missing'};
                        const body = {
                            pageSize, pageNum: 1, positionName: '', postCode: '',
                            postCodeList: '', workLocationList: '', workTypeList: ['3'],
                            positionTypeList: ['3'], deptCodeList: '', onlyHotRecruit: 0,
                            recruitType: 1, practiceTypes: ''
                        };
                        const requestHeaders = {...headers, 'Content-Type': 'application/json', 'X-CSRF': csrf.data};
                        const response = await fetch('/api/campus/position/positionList', {
                            method: 'POST', headers: requestHeaders, body: JSON.stringify(body)
                        });
                        return {status: response.status, payload: await response.json()};
                    }""",
                    {"pageSize": limit, "headers": API_HEADERS},
                )
                if payload.get("error"):
                    return CollectionResult([], False, response_urls, payload["error"])
                if payload.get("status") in {403, 429}:
                    return CollectionResult([], False, response_urls, f"http_{payload['status']}")
                data = ((payload.get("payload") or {}).get("data") or {})
                rows = data.get("list") or []
                if not rows:
                    return CollectionResult([], False, response_urls, "no_public_campus_positions")
                items = [
                    ListingItem(str(row.get("id")), _plain(row.get("positionName")),
                                f"https://jobs.bilibili.com/campus/positions/{row.get('id')}?type=3", row)
                    for row in rows if row.get("id") and row.get("positionName")
                ]
                return CollectionResult(items, False, response_urls)
            finally:
                await browser.close()

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                await page.goto(source["url"], wait_until="domcontentloaded", timeout=int(source.get("timeout_ms", 30000)))
                detail = await page.evaluate(
                    """async ({jobId, headers}) => {
                        const csrf = await (await fetch('/api/auth/v1/csrf/token', {headers})).json();
                        if (!csrf || !csrf.data) return {error: 'csrf_token_missing'};
                        const response = await fetch('/api/campus/position/detail/' + encodeURIComponent(jobId), {
                            headers: {...headers, 'X-CSRF': csrf.data}
                        });
                        return {status: response.status, payload: await response.json()};
                    }""",
                    {"jobId": item.source_job_id, "headers": API_HEADERS},
                )
                if detail.get("error"):
                    raise RuntimeError(detail["error"])
                if detail.get("status") in {403, 429}:
                    raise RuntimeError(f"http_{detail['status']}")
                payload = detail.get("payload") or {}
                data = payload.get("data") or {}
                if not data:
                    raise RuntimeError("public_position_detail_missing")
                return data
            finally:
                await browser.close()

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        return normalize_bilibili_position(raw, source)


__all__ = ["BilibiliCampusAdapter", "normalize_bilibili_position"]
