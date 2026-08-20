from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from playwright.async_api import async_playwright

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_job


class DewuCampusAdapter:
    """Adapter for Dewu's public campus portal (JSON listing + detail links)."""

    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(locale="zh-CN")
            payloads: list[dict[str, Any]] = []

            async def on_response(response):
                if "/api/v1/search/job/posts" not in response.url:
                    return
                try:
                    data = await response.json()
                    if isinstance(data, dict) and isinstance(data.get("data"), dict):
                        payloads.append(data["data"])
                except Exception:
                    return

            page.on("response", on_response)
            await page.goto(source["url"].rstrip("/") + "/position/list", wait_until="domcontentloaded", timeout=45000)
            await page.wait_for_timeout(4500)
            hrefs = await page.locator("a[data-id]").evaluate_all(
                "els => els.map(e => ({id: e.getAttribute('data-id'), href: e.getAttribute('href')}))"
            )
            page.remove_listener("response", on_response)
            await browser.close()

        href_by_id = {str(x.get("id")): x.get("href") for x in hrefs if x.get("id") and x.get("href")}
        rows: list[dict[str, Any]] = []
        seen: set[str] = set()
        for payload in payloads:
            for row in payload.get("job_post_list") or []:
                job_id = str(row.get("id") or "")
                if job_id and job_id not in seen:
                    seen.add(job_id)
                    row = dict(row)
                    row["detail_href"] = href_by_id.get(job_id)
                    rows.append(row)
        rows = rows[: int(source.get("max_jobs") or 10)]
        items = [
            ListingItem(str(row["id"]), str(row.get("title") or ""),
                        "https://campus.dewu.com" + row["detail_href"], row)
            for row in rows if row.get("id") and row.get("title") and row.get("detail_href")
        ]
        if not items:
            return CollectionResult([], False, [source["url"]], "no_concrete_visible_job_cards")
        return CollectionResult(items, False, [source["url"], "https://campus.dewu.com/api/v1/search/job/posts"])

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        return item.raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        payload = dict(raw)
        cities = [str(x.get("name") or x.get("i18n_name")) for x in payload.get("city_list") or [] if isinstance(x, dict)]
        function = payload.get("job_function") or {}
        recruitment = payload.get("recruit_type") or {}
        parent = recruitment.get("parent") or {}
        payload["city"] = " / ".join(x for x in cities if x)
        payload["category"] = function.get("name") or "未注明"
        payload["job_nature"] = "实习" if "实习" in str(parent.get("name") or "") or "实习" in str(recruitment.get("name") or "") else "全职"
        payload["degree"] = None
        payload["requirements"] = payload.get("requirement")
        payload["apply_url"] = "https://campus.dewu.com" + str(payload.get("detail_href"))
        payload["source_job_id"] = str(payload.get("id"))
        if payload.get("publish_time"):
            payload["published_at"] = datetime.fromtimestamp(float(payload["publish_time"]) / 1000, tz=timezone.utc).isoformat()
        job = normalize_job(payload, source)
        if not job:
            return None
        match = re.search(r"20\d{2}", str(payload.get("title") or "") + str(payload.get("job_subject") or ""))
        if match:
            job["graduate_year"] = match.group(0)
        return job
