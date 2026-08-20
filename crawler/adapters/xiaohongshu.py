from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from playwright.async_api import async_playwright

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_job


class XiaohongshuCampusAdapter:
    """Public Xiaohongshu campus position API adapter."""

    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(locale="zh-CN")
            payloads: list[dict[str, Any]] = []

            async def on_response(response):
                if "/pageQueryPosition" not in response.url:
                    return
                try:
                    data = await response.json()
                    if isinstance(data, dict) and isinstance(data.get("data"), dict):
                        payloads.append(data["data"])
                except Exception:
                    return

            page.on("response", on_response)
            await page.goto(source["url"], wait_until="domcontentloaded", timeout=45000)
            await page.wait_for_timeout(5000)
            page.remove_listener("response", on_response)
            await browser.close()

        rows: list[dict[str, Any]] = []
        seen: set[str] = set()
        for payload in payloads:
            for row in payload.get("list") or []:
                job_id = str(row.get("positionId") or "")
                if job_id and job_id not in seen:
                    seen.add(job_id)
                    rows.append(row)
        rows = rows[: int(source.get("max_jobs") or 10)]
        items = [
            ListingItem(str(row["positionId"]), str(row.get("positionName") or ""),
                        f"https://job.xiaohongshu.com/campus/position/{row['positionId']}", row)
            for row in rows if row.get("positionId") and row.get("positionName")
        ]
        if not items:
            return CollectionResult([], False, [source["url"]], "no_concrete_visible_job_cards")
        return CollectionResult(items, False, [source["url"], "https://job.xiaohongshu.com/websiterecruit/position/pageQueryPosition"])

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        return item.raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        payload = dict(raw)
        payload["title"] = payload.get("positionName")
        payload["city"] = str(payload.get("workplace") or "").replace("，", " / ")
        project = str(payload.get("jobProjectName") or "")
        payload["job_nature"] = "实习" if "实习" in project or "实习" in str(payload.get("positionName") or "") else "全职"
        payload["category"] = payload.get("jobType") or "未注明"
        payload["degree"] = None
        payload["requirements"] = payload.get("qualification")
        payload["description"] = payload.get("duty")
        payload["apply_url"] = f"https://job.xiaohongshu.com/campus/position/{payload.get('positionId')}"
        payload["source_job_id"] = str(payload.get("positionId"))
        if payload.get("publishTime"):
            try:
                payload["published_at"] = datetime.fromisoformat(str(payload["publishTime"])).replace(tzinfo=timezone.utc).isoformat()
            except ValueError:
                payload["published_at"] = str(payload["publishTime"])
        job = normalize_job(payload, source)
        if not job:
            return None
        match = re.search(r"20\d{2}", str(payload.get("positionName") or "") + project + str(payload.get("qualification") or ""))
        if match:
            job["graduate_year"] = match.group(0)
        return job
