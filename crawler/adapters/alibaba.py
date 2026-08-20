from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin

from playwright.async_api import async_playwright

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_job


class AlibabaCampusAdapter:
    """Adapter for Alibaba's public campus portal.

    The portal renders a public listing and detail page and obtains the
    concrete records through ordinary XHR requests.  We keep the browser
    session bounded (the initial source probe is capped by ``max_jobs``) and
    retain the detail payload as raw evidence for the normalizer.
    """

    def __init__(self) -> None:
        self._playwright = None
        self._browser = None
        self._page = None

    async def _ensure_page(self):
        if self._page is None:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=True)
            context = await self._browser.new_context(
                locale="zh-CN",
                viewport={"width": 1440, "height": 1000},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/126.0 Safari/537.36"
                ),
            )
            self._page = await context.new_page()
        return self._page

    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        page = await self._ensure_page()
        listing_url = "https://campus-talent.alibaba.com/campus/position?batchId=100000760001"
        payloads: list[dict[str, Any]] = []

        async def on_response(response):
            if "/position/search" not in response.url:
                return
            try:
                data = await response.json()
                content = data.get("content") if isinstance(data, dict) else None
                if isinstance(content, dict):
                    payloads.append(content)
            except Exception:
                return

        page.on("response", on_response)
        await page.goto(listing_url, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(5000)
        # A filtered business unit may not occur on page 1. Traverse only the
        # bounded number of public pages needed to fill the initial sample.
        max_pages = int(source.get("max_pages") or 1)
        for page_no in range(2, max_pages + 1):
            if len(payloads) and len(rows if 'rows' in locals() else []) >= int(source.get("max_jobs") or 10):
                break
            try:
                button = page.get_by_role("button", name=f"第{page_no}页，共49页")
                if await button.count() == 0:
                    break
                await button.click(timeout=3000)
                await page.wait_for_timeout(800)
            except Exception:
                break
        page.remove_listener("response", on_response)

        rows: list[dict[str, Any]] = []
        seen: set[str] = set()
        for payload in payloads:
            for row in payload.get("datas") or []:
                if not isinstance(row, dict):
                    continue
                circle_filter = str(source.get("circle_filter") or "").strip()
                if circle_filter and circle_filter not in (row.get("circleNames") or []):
                    continue
                job_id = str(row.get("id") or "").strip()
                if job_id and job_id not in seen:
                    seen.add(job_id)
                    rows.append(row)

        max_jobs = int(source.get("max_jobs") or 10)
        rows = rows[:max_jobs]
        items = [
            ListingItem(
                source_job_id=str(row["id"]),
                title=str(row.get("name") or ""),
                detail_url=urljoin(listing_url, f"/campus/position/{row['id']}"),
                raw=row,
            )
            for row in rows
            if row.get("id") and row.get("name")
        ]
        if not items:
            return CollectionResult([], False, [listing_url], "no_concrete_visible_job_cards")
        return CollectionResult(items, False, [listing_url, "https://campus-talent.alibaba.com/position/search"])

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        page = await self._ensure_page()
        payload: dict[str, Any] | None = None

        async def on_response(response):
            nonlocal payload
            if "/position/detail" not in response.url:
                return
            try:
                data = await response.json()
                if isinstance(data, dict) and isinstance(data.get("content"), dict):
                    payload = data["content"]
            except Exception:
                return

        page.on("response", on_response)
        await page.goto(item.detail_url, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(1200)
        page.remove_listener("response", on_response)
        if not payload:
            raise RuntimeError(f"Alibaba job detail unavailable: {item.detail_url}")
        payload["apply_url"] = item.detail_url
        payload["source_job_id"] = item.source_job_id
        return payload

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        payload = dict(raw)
        payload["title"] = payload.get("name")
        payload["city"] = " / ".join(payload.get("workLocations") or [])
        payload["job_nature"] = "全职" if payload.get("categoryType") == "freshman" else "实习"
        payload["category"] = payload.get("categoryName") or "未注明"
        payload["degree"] = payload.get("degree") or "未注明"
        payload["requirements"] = payload.get("requirement")
        payload["description"] = payload.get("description")
        payload["apply_url"] = payload.get("apply_url") or urljoin(
            source["url"], f"/campus/position/{payload.get('id')}"
        )
        payload["source_job_id"] = str(payload.get("source_job_id") or payload.get("id"))
        if payload.get("modifyTime"):
            payload["published_at"] = datetime.fromtimestamp(
                float(payload["modifyTime"]) / 1000, tz=timezone.utc
            ).isoformat()
        job = normalize_job(payload, source)
        if not job:
            return None
        batch = str(payload.get("batchName") or "")
        if "届" in batch:
            import re
            match = re.search(r"20\d{2}", batch)
            if match:
                job["graduate_year"] = match.group(0)
        return job
