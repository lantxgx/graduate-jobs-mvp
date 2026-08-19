"""OPPO public campus position-list adapter."""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from playwright.async_api import async_playwright

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_category, normalize_city, normalize_degree, normalize_job_nature


def _category(raw: dict[str, Any], title: str, text: str) -> str:
    explicit = str(raw.get("positionTypeName") or raw.get("positionType") or "").strip()
    direct = {
        "AI/算法类": "算法/AI",
        "软件类": "软件研发",
        "硬件类": "硬件研发",
        "工程技术类": "制造/工艺",
        "采购类": "供应链/采购",
        "品牌策划类": "市场/销售",
        "销售服务类": "市场/销售",
        "综合职能类": "职能",
        "设计类": "设计",
        "产品类": "产品",
        "业务支撑类": "运营",
    }
    return direct.get(explicit) or normalize_category(explicit, title, text)


def _detail_url(source: dict[str, Any], position_id: str) -> str:
    parts = urlsplit(source["url"])
    return urlunsplit((parts.scheme, parts.netloc, "/university/oppo/campus/post/" + position_id, "", ""))


def normalize_oppo_job(raw: dict[str, Any], source: dict[str, Any]) -> dict[str, Any] | None:
    position_id = str(raw.get("idRecruitPosition") or raw.get("idProjPosition") or "").strip()
    title = str(raw.get("positionName") or raw.get("projectPositionName") or "").strip()
    description = str(raw.get("positionDesc") or raw.get("projectPositionDesc") or "").strip()
    requirements = str(raw.get("positionRequire") or raw.get("projectPositionRequire") or "").strip()
    if not position_id or not title or not (description or requirements):
        return None
    raw_nature = str(raw.get("recruitmentTypeName") or raw.get("recruitmentType") or "")
    nature = normalize_job_nature(raw_nature, title, description + " " + requirements)
    if nature is None:
        return None
    city = str(raw.get("workCityName") or "").strip() or None
    canonical = {
        "company": source["company"],
        "title": title[:160],
        "city": normalize_city(city),
        "job_nature": nature,
        "category": _category(raw, title, description + " " + requirements),
        "degree": normalize_degree(None, requirements),
        "graduate_year": None,
        "requirements": requirements or None,
        "description": description or None,
        "apply_url": _detail_url(source, position_id),
        "source_url": source["url"],
        "source_job_id": position_id,
        "published_at": str(raw.get("releaseTime") or "") or None,
    }
    digest = "|".join(str(canonical.get(key) or "") for key in (
        "company", "title", "city", "job_nature", "source_job_id", "apply_url"
    ))
    canonical["content_hash"] = hashlib.sha256(digest.encode("utf-8", "ignore")).hexdigest()
    canonical["source_id"] = source["id"]
    canonical["raw"] = raw
    return canonical


class OppoAdapter:
    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        payload: dict[str, Any] | None = None
        response_urls: list[str] = []
        blocked: str | None = None
        max_jobs = min(max(int(source.get("max_jobs", 20)), 1), 20)
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()

            async def on_response(response):
                nonlocal payload, blocked
                if "/openapi/position/pageNew" not in response.url:
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
                navigation = await page.goto(source["url"], wait_until="domcontentloaded", timeout=30000)
                if navigation and navigation.status in {403, 429}:
                    blocked = f"http_{navigation.status}"
                await page.wait_for_timeout(5000)
            finally:
                await browser.close()
        if blocked:
            return CollectionResult([], False, response_urls, blocked)
        if not payload:
            return CollectionResult([], False, response_urls, "public_job_list_missing")
        data = payload.get("data") or {}
        records = data.get("records") if isinstance(data, dict) else None
        if not isinstance(records, list):
            return CollectionResult([], False, response_urls, "public_job_list_invalid")
        items: list[ListingItem] = []
        for raw in records[:max_jobs]:
            if not isinstance(raw, dict):
                continue
            position_id = str(raw.get("idRecruitPosition") or raw.get("idProjPosition") or "").strip()
            if not position_id:
                continue
            items.append(ListingItem(position_id, str(raw.get("positionName") or ""), _detail_url(source, position_id), raw))
        total = int(data.get("total") or data.get("count") or len(records)) if isinstance(data, dict) else len(records)
        return CollectionResult(items, total <= len(items), response_urls)

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        return item.raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        return normalize_oppo_job(raw, source)


__all__ = ["OppoAdapter", "normalize_oppo_job"]
