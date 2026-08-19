from __future__ import annotations

import asyncio
import os
import re
from typing import Any
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright


POSITION_LINK_RE = re.compile(r"/position/(\d+)/detail/?$")
BLOCKED_STATUSES = {403, 429}
BLOCKED_MARKERS = ("验证码", "访问过于频繁", "安全验证", "captcha")
JOB_NATURE_MARKERS = ("正式", "全职", "实习", "兼职", "其他")


def parse_feishu_detail_text(text: str, apply_url: str) -> dict[str, Any] | None:
    """Parse the stable visible-field order used by Feishu recruitment details."""
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    try:
        description_index = lines.index("职位描述")
        requirements_index = lines.index("职位要求")
    except ValueError:
        return None

    if description_index < 2 or requirements_index <= description_index:
        return None

    match = POSITION_LINK_RE.search(urlparse(apply_url).path)
    if not match:
        return None

    requirement_lines = lines[requirements_index + 1 :]
    if requirement_lines and requirement_lines[-1] in {"投递", "立即投递"}:
        requirement_lines.pop()

    description = "\n".join(lines[description_index + 1 : requirements_index]).strip()
    requirements = "\n".join(requirement_lines).strip()
    if not description or not requirements:
        return None

    header_lines = lines[:description_index]
    if len(header_lines) >= 4:
        title = header_lines[0]
        city = header_lines[1]
        job_nature = header_lines[2]
        category = " ".join(header_lines[3:])
    elif len(header_lines) == 2:
        title = header_lines[0]
        metadata = header_lines[1]
        nature_match = re.match(
            rf"^(.*?)({'|'.join(JOB_NATURE_MARKERS)})(.+)$", metadata
        )
        if not nature_match:
            return None
        city, job_nature, category = (
            nature_match.group(1).strip(),
            nature_match.group(2).strip(),
            nature_match.group(3).strip(),
        )
    else:
        return None

    if not all((title, city, job_nature, category)):
        return None

    return {
        "id": match.group(1),
        "title": title,
        "city": city,
        "recruitment_type": job_nature,
        "category": category,
        "description": description,
        "requirements": requirements,
        "apply_url": apply_url,
    }


async def discover_feishu_jobs(
    url: str,
    timeout_ms: int | None = None,
    max_jobs: int | None = None,
    job_delay_ms: int | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Read a small number of public campus jobs from a Feishu recruitment site.

    The minimal harness unit intentionally reads only the first N visible positions.
    It performs no retries and stops immediately on 403, 429, or verification pages.
    """
    timeout_ms = timeout_ms or int(os.getenv("CRAWL_TIMEOUT_MS", "45000"))
    max_jobs = max_jobs or int(os.getenv("FEISHU_MAX_JOBS", "5"))
    job_delay_ms = job_delay_ms or int(os.getenv("FEISHU_JOB_DELAY_MS", "1200"))

    jobs: list[dict[str, Any]] = []
    seen_urls: list[str] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            locale="zh-CN",
            viewport={"width": 1440, "height": 1000},
            user_agent=(
                "GraduateRadar/0.1 (public campus recruitment aggregation; "
                "low-frequency contact: local-operator)"
            ),
        )
        page = await context.new_page()

        try:
            response = await page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            if response and response.status in BLOCKED_STATUSES:
                raise RuntimeError(f"Feishu recruitment site returned HTTP {response.status}")
            body_text = (await page.locator("body").inner_text()).lower()
            if any(marker.lower() in body_text for marker in BLOCKED_MARKERS):
                raise RuntimeError("Feishu recruitment site requested verification")

            anchors = page.locator('a[href*="/position/"][href*="/detail"]')
            try:
                await anchors.first.wait_for(
                    state="attached", timeout=min(timeout_ms, 10_000)
                )
            except Exception as exc:
                raise RuntimeError(
                    "No concrete Feishu campus job links were found"
                ) from exc
            hrefs: list[str] = []
            for index in range(await anchors.count()):
                href = await anchors.nth(index).get_attribute("href")
                if not href:
                    continue
                detail_url = urljoin(url, href)
                if POSITION_LINK_RE.search(urlparse(detail_url).path) and detail_url not in hrefs:
                    hrefs.append(detail_url)
                if len(hrefs) >= max_jobs:
                    break

            if not hrefs:
                raise RuntimeError("No concrete Feishu campus job links were found")

            for detail_url in hrefs:
                if jobs:
                    await page.wait_for_timeout(max(job_delay_ms, 0))
                response = await page.goto(
                    detail_url, wait_until="domcontentloaded", timeout=timeout_ms
                )
                seen_urls.append(detail_url)
                if response and response.status in BLOCKED_STATUSES:
                    raise RuntimeError(
                        f"Feishu recruitment site returned HTTP {response.status}"
                    )
                try:
                    await page.get_by_text("职位要求", exact=True).wait_for(
                        state="visible", timeout=min(timeout_ms, 10_000)
                    )
                except Exception as exc:
                    raise RuntimeError(
                        f"Feishu job detail did not finish rendering: {detail_url}"
                    ) from exc
                main_text = await page.locator("main").inner_text()
                lowered = main_text.lower()
                if any(marker.lower() in lowered for marker in BLOCKED_MARKERS):
                    raise RuntimeError("Feishu recruitment site requested verification")
                parsed = parse_feishu_detail_text(main_text, detail_url)
                if parsed:
                    jobs.append(parsed)
                else:
                    raise RuntimeError(
                        f"Feishu job detail failed the field quality gate: {detail_url}"
                    )
        finally:
            await browser.close()

    if not jobs:
        raise RuntimeError("Feishu job crawl produced zero qualified positions")
    return jobs, seen_urls
