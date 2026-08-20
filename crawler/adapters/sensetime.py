"""Browser-backed adapter for SenseTime's public Feishu ATS campus portal.

The public page generates a request signature in the browser.  We let the
normal page load make that request and parse its JSON response, rather than
reproducing or bypassing the signing mechanism.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any
from urllib.parse import urljoin

from playwright.async_api import async_playwright

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_category, normalize_degree, normalize_job, normalize_job_nature, normalize_location_name


class SensetimeCampusAdapter:
    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        max_jobs = min(max(int(source.get("max_jobs", 10)), 1), 20)
        payload: dict[str, Any] | None = None
        response_urls: list[str] = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(locale="zh-CN", user_agent="Mozilla/5.0")

            async def on_response(resp: Any) -> None:
                nonlocal payload
                if "/api/v1/search/job/posts" not in resp.url or resp.request.method != "POST":
                    return
                response_urls.append(resp.url)
                try:
                    if resp.status == 200:
                        body = await resp.text()
                        candidate = json.loads(body)
                        if isinstance(candidate, dict) and isinstance((candidate.get("data") or {}).get("job_post_list"), list):
                            payload = candidate
                except Exception:
                    return

            page.on("response", on_response)
            try:
                await page.goto(source["url"], wait_until="domcontentloaded", timeout=int(source.get("timeout_ms", 60000)))
                await page.wait_for_timeout(int(source.get("render_wait_ms", 8000)))
            finally:
                await browser.close()
        rows = ((payload or {}).get("data") or {}).get("job_post_list") or []
        if not rows:
            return CollectionResult([], False, response_urls, "no_concrete_visible_job_cards")
        items: list[ListingItem] = []
        for row in rows[:max_jobs]:
            if not isinstance(row, dict) or not row.get("id") or not row.get("title"):
                continue
            detail_url = urljoin(source["url"], f"/edu/position/{row['id']}/detail")
            items.append(ListingItem(str(row["id"]), str(row["title"]), detail_url, row))
        return CollectionResult(items, False, response_urls)

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        # The public search response already contains the full description and
        # requirements; no authenticated detail call is needed.
        return item.raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        title = str(raw.get("title") or "").strip()
        description = str(raw.get("description") or "").strip()
        requirements = str(raw.get("requirement") or "").strip()
        if not title or not (description or requirements):
            return None
        cities: list[str] = []
        for city in raw.get("city_list") or []:
            name = normalize_location_name(str((city or {}).get("name") or ""))
            if name and name not in cities:
                cities.append(name)
        city = " / ".join(cities) or None
        recruit_name = str((raw.get("recruit_type") or {}).get("name") or "校园招聘")
        nature = normalize_job_nature(recruit_name, title, f"{description} {requirements}")
        if not nature:
            return None
        category_name = str((raw.get("job_category") or {}).get("name") or "")
        item = {
            "company": source["company"],
            "title": title,
            "city": city,
            "job_nature": nature,
            "category": normalize_category(category_name, title, f"{description} {requirements}"),
            "degree": normalize_degree(None, requirements),
            "graduate_year": None,
            "requirements": requirements,
            "description": description,
            "apply_url": urljoin(source["url"], f"/edu/position/{raw['id']}/detail"),
            "source_url": source["url"],
            "source_job_id": str(raw["id"]),
            "published_at": raw.get("publish_time"),
        }
        digest = "|".join(str(item.get(k) or "") for k in ("company", "title", "city", "job_nature", "source_job_id", "apply_url", "description", "requirements"))
        item["content_hash"] = hashlib.sha256(digest.encode("utf-8", "ignore")).hexdigest()
        item["source_id"] = source["id"]
        item["raw"] = raw
        return normalize_job(item, source)


class BytedanceAtsCampusAdapter(SensetimeCampusAdapter):
    """Same public browser contract used by ByteDance ATS tenant portals."""


__all__ = ["SensetimeCampusAdapter", "BytedanceAtsCampusAdapter"]
