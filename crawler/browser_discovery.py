from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from playwright.async_api import async_playwright

from crawler.normalize import find_job_dicts


BLOCKED_STATUSES = {403, 429}
BLOCKED_MARKERS = ("captcha", "验证码", "安全验证", "访问过于频繁", "robot check")


def blocked_signal(status: int | None, text: str = "") -> str | None:
    if status in BLOCKED_STATUSES:
        return f"HTTP {status}"
    lowered = (text or "").lower()
    for marker in BLOCKED_MARKERS:
        if marker.lower() in lowered:
            return f"verification marker: {marker}"
    return None


async def discover_job_json(url: str, timeout_ms: int | None = None) -> tuple[list[dict[str, Any]], list[str]]:
    """
    Open a public recruitment page in Chromium, listen to XHR/fetch JSON responses,
    and recursively search those JSON payloads for job-like objects.

    This is intentionally generic. For a high-volume source, replace it later with
    a source-specific adapter that calls the discovered public JSON endpoint directly.
    """
    timeout_ms = timeout_ms or int(os.getenv("CRAWL_TIMEOUT_MS", "45000"))
    payloads: list[Any] = []
    response_urls: list[str] = []
    blocked_reason: str | None = None

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            locale="zh-CN",
            viewport={"width": 1440, "height": 1000},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

        async def handle_response(response):
            nonlocal blocked_reason
            signal = blocked_signal(response.status)
            if signal:
                blocked_reason = signal
                return
            try:
                content_type = (response.headers.get("content-type") or "").lower()
                resource_type = response.request.resource_type
                if "json" not in content_type and resource_type not in {"xhr", "fetch"}:
                    return
                text = await response.text()
                if len(text) > 8_000_000:
                    return
                data = json.loads(text)
                payloads.append(data)
                response_urls.append(response.url)
            except Exception:
                return

        page.on("response", handle_response)

        try:
            response = await page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            blocked_reason = blocked_reason or blocked_signal(response.status if response else None)
        except Exception:
            # SPA pages can still be useful even when the final navigation state times out.
            pass

        if not blocked_reason:
            try:
                blocked_reason = blocked_signal(None, await page.locator("body").inner_text())
            except Exception:
                pass
        if blocked_reason:
            raise RuntimeError(f"Recruitment site access blocked: {blocked_reason}")

        # Give apps time to issue XHR/fetch requests.
        await page.wait_for_timeout(min(7000, max(2500, timeout_ms // 6)))

        # Scroll to trigger lazy-loaded job lists.
        for _ in range(5):
            await page.mouse.wheel(0, 1400)
            await page.wait_for_timeout(700)

        # Click likely "jobs / positions / more" controls if they exist.
        for label in ["职位", "岗位", "Jobs", "更多职位", "查看职位", "校园招聘"]:
            try:
                locator = page.get_by_text(label, exact=False).first
                if await locator.count():
                    await locator.click(timeout=1200)
                    await page.wait_for_timeout(1000)
            except Exception:
                pass

        if blocked_reason:
            raise RuntimeError(f"Recruitment site access blocked: {blocked_reason}")
        await browser.close()

    jobs: list[dict[str, Any]] = []
    seen = set()
    for payload in payloads:
        for item in find_job_dicts(payload):
            sig = json.dumps(item, ensure_ascii=False, sort_keys=True, default=str)
            if sig not in seen:
                seen.add(sig)
                jobs.append(item)

    return jobs, sorted(set(response_urls))


def run_discovery(url: str):
    return asyncio.run(discover_job_json(url))
