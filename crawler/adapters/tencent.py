from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from playwright.async_api import async_playwright

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_job


class TencentCampusAdapter:
    """Public Tencent campus list/detail adapter."""

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
        payloads: list[dict[str, Any]] = []

        async def on_response(response):
            if "/position/searchPosition" not in response.url:
                return
            try:
                data = await response.json()
                if isinstance(data, dict) and isinstance(data.get("data"), dict):
                    payloads.append(data["data"])
            except Exception:
                return

        page.on("response", on_response)
        await page.goto(source["url"], wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(4500)
        page.remove_listener("response", on_response)
        rows: list[dict[str, Any]] = []
        seen: set[str] = set()
        for payload in payloads:
            for row in payload.get("positionList") or []:
                post_id = str(row.get("postId") or "").strip()
                if post_id and post_id not in seen:
                    seen.add(post_id)
                    rows.append(row)
        rows = rows[: int(source.get("max_jobs") or 10)]
        items = [
            ListingItem(str(row["postId"]), str(row.get("positionTitle") or ""),
                        f"https://join.qq.com/post_detail.html?postid={row['postId']}", row)
            for row in rows if row.get("postId") and row.get("positionTitle")
        ]
        if not items:
            return CollectionResult([], False, [source["url"]], "no_concrete_visible_job_cards")
        return CollectionResult(items, False, [source["url"], "https://join.qq.com/api/v1/position/searchPosition"])

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        page = await self._ensure_page()
        payload: dict[str, Any] | None = None

        async def on_response(response):
            nonlocal payload
            if "/jobDetails/getJobDetailsByPostId" not in response.url:
                return
            try:
                data = await response.json()
                if isinstance(data, dict) and isinstance(data.get("data"), dict):
                    payload = data["data"]
            except Exception:
                return

        page.on("response", on_response)
        await page.goto(item.detail_url, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(1000)
        page.remove_listener("response", on_response)
        if not payload:
            raise RuntimeError(f"Tencent job detail unavailable: {item.detail_url}")
        payload["apply_url"] = item.detail_url
        payload["source_job_id"] = item.source_job_id
        return payload

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        payload = dict(raw)
        payload["title"] = payload.get("title")
        payload["city"] = " / ".join(payload.get("workCityList") or [])
        payload["job_nature"] = "实习" if "实习" in str(payload.get("recruitTypeName") or "") else "全职"
        payload["category"] = payload.get("tidName") or "未注明"
        payload["degree"] = "未注明"
        payload["requirements"] = payload.get("request")
        payload["description"] = payload.get("desc")
        payload["apply_url"] = payload.get("apply_url")
        payload["source_job_id"] = str(payload.get("source_job_id") or payload.get("postId"))
        payload["graduate_year"] = "2027" if "应届" in str(payload.get("projectName") or "") else None
        job = normalize_job(payload, source)
        if not job:
            return None
        job["graduate_year"] = payload.get("graduate_year")
        return job
