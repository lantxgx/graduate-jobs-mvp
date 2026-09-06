"""Bounded adapter for the public Trip.com Group campus job API."""

from __future__ import annotations

import hashlib
import html
import re
from typing import Any

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_job


def _text(value: Any) -> str:
    soup = BeautifulSoup(html.unescape(str(value or "")), "html.parser")
    return re.sub(r"\s+", " ", soup.get_text(" ", strip=True)).strip()


def _sections(value: Any) -> tuple[str, str]:
    text = _text(value)
    req = re.search(r"(我们期望你|We are looking for|任职要求|岗位要求)\s*[:：]?", text, re.I)
    duty = re.search(r"(你将会负责|You will be responsible for|岗位职责|工作职责)\s*[:：]?", text, re.I)
    if not req:
        return (text, text)
    requirements = text[req.start() :].strip()
    if duty and duty.start() < req.start():
        description = text[duty.end() : req.start()].strip()
    else:
        description = text[: req.start()].strip()
    return description or text, requirements


def _city(row: dict[str, Any], evidence: str) -> str:
    value = _text(row.get("cityName"))
    if value:
        return value
    match = re.search(r"工作地点\s*[:：]\s*(?:中国|英国|德国|法国)?\s*(伦敦|上海|北京|南通|广州|深圳|成都|杭州|西安|南京|武汉|重庆|厦门|苏州|济南|桂林)", evidence)
    return match.group(1) if match else ""


def normalize_ctrip_job(raw: dict[str, Any], source: dict[str, Any]) -> dict[str, Any] | None:
    title = _text(raw.get("jobTitle"))
    source_id = _text(raw.get("fromId") or raw.get("jobId") or raw.get("id"))
    title = re.sub(r"\s*\([A-Z]{2}\d+\)\s*$", "", title).strip()
    evidence = _text(raw.get("requirements"))
    description, requirements = _sections(raw.get("requirements"))
    category = _text(raw.get("jobFamilyGroupName"))
    if category.lower() in {"ai & bi", "ai&bi"} and "数据" in title:
        category = "数据"
    canonical_raw = {
        "id": source_id,
        "title": title,
        "city": _city(raw, evidence),
        "job_type": _text(raw.get("kindName") or "应届校招生"),
        "category": category,
        "degree": "",
        "description": description,
        "requirements": requirements,
        "published_at": raw.get("publishDate"),
        "detail_url": f"https://careers.ctrip.com/#/campus/job-detail/{source_id}",
    }
    if not all((source_id, title, canonical_raw["city"], description, requirements)):
        return None
    job = normalize_job(canonical_raw, source)
    if not job:
        return None
    job["raw"] = raw
    year = re.search(r"(20\d{2})\s*届|class of\s*(20\d{2})", f"{title} {evidence}", re.I)
    if year:
        job["graduate_year"] = next(group for group in year.groups() if group)
    return job


class CtripCampusAdapter:
    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        limit = min(max(int(source.get("max_jobs", 20)), 1), 20)
        response_urls = [source["url"], "https://careers.ctrip.com/api/hrrecruit/getJobAd"]
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                response = await page.goto(source["url"], wait_until="domcontentloaded", timeout=30000)
                if response and response.status in {403, 429}:
                    return CollectionResult([], False, response_urls, f"http_{response.status}")
                payload = await page.evaluate(
                    """async ({size}) => {
                        const body = {condition:{fromId:[],keyword:'',kind:['1'],country:[],city:[],bucode:[],jobFamilyCode:[],jobFamilyGroupCode:[],category:2},pager:{index:'1',size:String(size)},head:{language:'zh_CN',version:'1'}};
                        const r = await fetch('/api/hrrecruit/getJobAd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
                        return {status:r.status,payload:await r.json()};
                    }""",
                    {"size": limit},
                )
                if payload.get("status") in {403, 429}:
                    return CollectionResult([], False, response_urls, f"http_{payload['status']}")
                rows = ((payload.get("payload") or {}).get("retValue") or {}).get("recruitJobAdList") or []
                items = [
                    ListingItem(str(row.get("fromId") or row.get("jobId")), _text(row.get("jobTitle")),
                                f"https://careers.ctrip.com/#/campus/job-detail/{row.get('fromId') or row.get('jobId')}", row)
                    for row in rows if row.get("fromId") or row.get("jobId")
                ]
                if not items:
                    return CollectionResult([], False, response_urls, "no_public_campus_positions")
                return CollectionResult(items, False, response_urls)
            finally:
                await browser.close()

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        return item.raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        return normalize_ctrip_job(raw, source)


__all__ = ["CtripCampusAdapter", "normalize_ctrip_job"]
