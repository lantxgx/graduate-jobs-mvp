from __future__ import annotations

import asyncio
import math
import os
from typing import Any

from playwright.async_api import async_playwright


LIST_ENDPOINT_MARKER = "/api/v1/search/job/posts"


async def discover_xiaomi_jobs(
    url: str,
    timeout_ms: int | None = None,
    max_pages: int | None = None,
    page_delay_ms: int | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Collect Xiaomi job posts from the public recruitment site's own list API.

    The API request is signed by Xiaomi's frontend. We let the public page issue
    those requests and only read the JSON responses, avoiding signature spoofing
    and one-detail-request-per-job crawling.

    ``max_pages=0`` means all available pages. A positive value limits the crawl
    to the newest N pages (10 jobs per page at the time of writing).
    """

    timeout_ms = timeout_ms or int(os.getenv("CRAWL_TIMEOUT_MS", "45000"))
    if max_pages is None:
        max_pages = int(os.getenv("XIAOMI_MAX_PAGES", "5"))
    if page_delay_ms is None:
        page_delay_ms = int(os.getenv("XIAOMI_PAGE_DELAY_MS", "1200"))

    response_urls: list[str] = []
    payload_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            locale="zh-CN",
            viewport={"width": 1440, "height": 1000},
            user_agent=(
                "GraduateRadar/0.1 (public recruitment aggregation; "
                "low-frequency contact: local-operator)"
            ),
        )
        page = await context.new_page()

        async def handle_response(response):
            if LIST_ENDPOINT_MARKER not in response.url:
                return
            response_urls.append(response.url.split("?", 1)[0])
            try:
                data = await response.json()
            except Exception:
                # The site may first return a CSRF challenge and then retry.
                return
            job_list = ((data.get("data") or {}).get("job_post_list") or [])
            if data.get("code") == 0 and isinstance(job_list, list):
                await payload_queue.put(data)

        page.on("response", handle_response)

        try:
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            except Exception:
                # The signed API request can still complete after a SPA timeout.
                pass

            first_payload = await asyncio.wait_for(
                payload_queue.get(), timeout=max(15, timeout_ms / 1000)
            )
            payloads = [first_payload]
            first_data = first_payload.get("data") or {}
            first_jobs = first_data.get("job_post_list") or []
            page_size = max(len(first_jobs), 1)
            total_count = int(first_data.get("count") or len(first_jobs))
            total_pages = max(1, math.ceil(total_count / page_size))
            pages_to_fetch = total_pages if max_pages == 0 else min(total_pages, max_pages)

            for _ in range(2, pages_to_fetch + 1):
                next_page = page.locator(
                    "li.atsx-pagination-next:not(.atsx-pagination-disabled)"
                )
                if await next_page.count() == 0:
                    break
                await page.wait_for_timeout(max(page_delay_ms, 0))
                await next_page.click(timeout=5000)
                payload = await asyncio.wait_for(
                    payload_queue.get(), timeout=max(15, timeout_ms / 1000)
                )
                payloads.append(payload)
        finally:
            await browser.close()

    jobs: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for payload in payloads:
        for item in ((payload.get("data") or {}).get("job_post_list") or []):
            if not isinstance(item, dict):
                continue
            job_id = str(item.get("id") or "")
            if not job_id or job_id in seen_ids:
                continue
            seen_ids.add(job_id)
            jobs.append(item)

    return jobs, sorted(set(response_urls))
