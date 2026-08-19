"""Visible HTML job-card adapter for custom company career pages.

This is a conservative fallback for self-hosted sites.  It parses only the
rendered page DOM and explicit links already present on a concrete job card;
it does not discover hidden API routes or manufacture detail URLs.
"""

from __future__ import annotations

import hashlib
import html
import re
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
from playwright.async_api import async_playwright

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import JOB_NATURE_VALUES, normalize_job


BLOCKED_MARKERS = ("captcha", "验证码", "security verification", "安全验证", "访问过于频繁")
CARD_HINTS = ("job", "position", "opening", "role", "career", "loop")


def _clean(value: Any) -> str:
    text = html.unescape(str(value or ""))
    return re.sub(r"\s+", " ", text).strip()


def _attr(node: Tag, names: tuple[str, ...]) -> str:
    for name in names:
        value = node.get(name)
        if value:
            return _clean(value)
    return ""


def _class_text(node: Tag, fragments: tuple[str, ...]) -> str:
    for element in node.select("[class]"):
        classes = " ".join(element.get("class") or []).lower()
        if any(fragment in classes for fragment in fragments):
            value = _clean(element.get_text(" ", strip=True))
            if value:
                return value
    return ""


def _card_for(anchor: Tag) -> Tag | None:
    # Start at the containing element; link classes such as ``job-link`` are
    # navigation affordances, not evidence that the link itself is a card.
    current: Tag | None = anchor.parent if isinstance(anchor.parent, Tag) else None
    for _ in range(6):
        if current is None:
            return None
        classes = " ".join(current.get("class") or []).lower()
        # A generic article/li is not sufficient: career pages also use those
        # elements for navigation cards and program marketing blocks.  Require
        # an explicit job/position/opening marker on the card itself.
        if any(hint in classes for hint in CARD_HINTS):
            return current
        current = current.parent if isinstance(current.parent, Tag) else None
    return None


def _title(card: Tag, anchor: Tag) -> str:
    for node in card.select("[data-title], h1, h2, h3, h4, h5, .title, [class*='title']"):
        value = _clean(node.get("data-title") or node.get_text(" ", strip=True))
        if 2 < len(value) <= 160 and value.lower() not in {"jobs", "careers", "view job", "查看职位"}:
            return value
    value = _clean(anchor.get_text(" ", strip=True))
    return value[:160]


def parse_visible_job_cards(page_html: str, source: dict[str, Any], max_jobs: int = 20) -> list[dict[str, Any]]:
    soup = BeautifulSoup(page_html, "html.parser")
    jobs: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    for anchor in soup.select("a[href]"):
        href = _clean(anchor.get("href"))
        if not href or href.startswith(("#", "javascript:", "mailto:")):
            continue
        card = _card_for(anchor)
        if card is None:
            continue
        detail_url = urljoin(source["url"], href)
        if not detail_url.startswith(("https://", "http://")) or detail_url in seen_urls:
            continue
        title = _title(card, anchor)
        if not title:
            continue
        card_text = _clean(card.get_text(" ", strip=True))
        city = _attr(card, ("data-location", "data-city")) or _class_text(card, ("location", "city"))
        nature = _attr(card, ("data-job-type", "data-employment-type", "data-type")) or _class_text(card, ("job-type", "employment", "type"))
        category = _attr(card, ("data-team", "data-department", "data-category")) or _class_text(card, ("team", "department", "category"))
        description = _class_text(card, ("description", "summary", "excerpt"))
        if not description and len(card_text) > len(title) + 20:
            description = card_text
        job_id = _attr(card, ("data-job-id", "data-position-id", "id")) or detail_url
        raw = {
            "id": job_id,
            "title": title,
            "city": city,
            "job_type": nature,
            "category": category,
            "description": description,
            "detail_url": detail_url,
        }
        canonical = normalize_job(raw, source)
        # The product deliberately has only two recruitment types.  A visible
        # card without an explicit, normalizable type is rejected rather than
        # being silently treated as an active job.
        if canonical and canonical.get("job_nature") in JOB_NATURE_VALUES:
            seen_urls.add(detail_url)
            jobs.append(canonical)
        if len(jobs) >= max(1, min(max_jobs, 20)):
            break
    return jobs


class CustomHtmlAdapter:
    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        max_jobs = min(max(int(source.get("max_jobs", 20)), 1), 20)
        response_urls = [source["url"]]
        stop_reason: str | None = None
        html_text = ""
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                response = await page.goto(
                    source["url"],
                    wait_until="domcontentloaded",
                    timeout=int(source.get("timeout_ms", 30000)),
                )
                if response and response.status in {403, 429}:
                    stop_reason = f"http_{response.status}"
                await page.wait_for_timeout(min(max(int(source.get("render_wait_ms", 1500)), 0), 5000))
                body = (await page.locator("body").inner_text()).lower()
                if any(marker.lower() in body for marker in BLOCKED_MARKERS):
                    stop_reason = "verification_page_detected"
                html_text = await page.content()
            finally:
                await browser.close()
        if stop_reason:
            return CollectionResult([], False, response_urls, stop_reason)
        jobs = parse_visible_job_cards(html_text, source, max_jobs)
        items = [ListingItem(job["source_job_id"], job["title"], job["apply_url"], job["raw"]) for job in jobs]
        if not items:
            return CollectionResult([], False, response_urls, "no_concrete_visible_job_cards")
        return CollectionResult(items, bool(source.get("snapshot_complete")), response_urls)

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        return item.raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        return normalize_job(raw, source)


__all__ = ["CustomHtmlAdapter", "parse_visible_job_cards"]
