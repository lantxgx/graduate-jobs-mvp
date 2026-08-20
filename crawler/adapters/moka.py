"""Bounded adapter for Moka (mokahr) public campus recruitment portals.

Moka's public job endpoints (``group-by-job``, ``jobs/v2``, ``jobs/module``)
all return AES-CBC encrypted payloads that are decrypted by the front-end
bundle, so this adapter does not try to reverse that.  Instead it drives the
rendered SPA directly: it opens the campus ``#/jobs`` route, waits for the job
cards to render, and extracts each card plus its detail page from the visible
DOM.  Requests stay sequential and bounded per run.

Only canonical public routes are used: ``#/jobs`` (list) and ``#/job/{jobId}``
(detail).  The adapter never bypasses logins, captchas or access controls.
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import re
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from playwright.async_api import async_playwright

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_category, normalize_city, normalize_degree, normalize_job_nature, normalize_location_name


BLOCKED_MARKERS = ("captcha", "验证码", "安全验证", "访问过于频繁", "robot check", "页面不存在")
JOB_HASH_RE = re.compile(r"#/job/([0-9a-fA-F-]{36})")
CITY_MARKERS = (
    "北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "武汉", "西安", "苏州",
    "珠海", "厦门", "天津", "重庆", "长沙", "合肥", "青岛", "济南", "沈阳", "大连",
    "福州", "郑州", "无锡", "宁波", "东莞", "佛山", "昆明", "兰州", "哈尔滨",
    "长春", "石家庄", "南昌", "贵阳", "太原", "南宁", "乌鲁木齐", "海口", "呼和浩特",
)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def _list_url(source: dict[str, Any]) -> str:
    parts = urlsplit(source["url"])
    # urlunsplit adds the leading "#" for the fragment field, so pass it
    # without the hash (otherwise we'd emit "##/jobs").
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", "/jobs"))


def _detail_page_url(source: dict[str, Any], job_id: str) -> str:
    parts = urlsplit(source["url"])
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", f"/job/{job_id}"))


def _blocked(text: str) -> str | None:
    for marker in BLOCKED_MARKERS:
        if marker.lower() in (text or "").lower():
            return f"blocked_marker:{marker}"
    return None


async def _collect_cards(page: Any, timeout_ms: int) -> tuple[list[dict[str, Any]], str | None]:
    """Wait for job-card links on the rendered page and parse them."""
    cards: dict[str, dict[str, Any]] = {}
    deadline = asyncio.get_event_loop().time() + timeout_ms / 1000
    while asyncio.get_event_loop().time() < deadline:
        try:
            body_text = await page.locator("body").inner_text(timeout=3000)
        except Exception:
            body_text = ""
        blocked = _blocked(body_text)
        if blocked:
            return [], blocked
        try:
            anchors = await page.locator("a[href*='#/job/']").evaluate_all(
                "els => els.map(e => ({href: e.getAttribute('href') || '', txt: (e.innerText || '').trim()}))"
            )
        except Exception:
            anchors = []
        new_count = 0
        for a in anchors:
            m = JOB_HASH_RE.search(a["href"])
            if not m:
                continue
            job_id = m.group(1)
            if job_id in cards:
                continue
            cards[job_id] = {"source_job_id": job_id, "raw_text": a["txt"]}
            new_count += 1
        if new_count:
            try:
                await page.mouse.wheel(0, 2500)
            except Exception:
                pass
        try:
            await page.wait_for_timeout(1200)
        except Exception:
            pass
        if len(cards) >= 60:
            break
    if not cards:
        return [], "public_job_list_missing"
    return list(cards.values()), None


def _parse_card(card: dict[str, Any]) -> dict[str, Any]:
    lines = [ln.strip() for ln in card["raw_text"].splitlines() if ln.strip()]
    meaningful = [ln for ln in lines if ln not in ("急", "分享", "|")]
    title = meaningful[0] if meaningful else card["source_job_id"]
    nature = "全职"
    city: str | None = None
    for ln in meaningful:
        if "实习" in ln or "Intern" in ln:
            nature = "实习"
        elif "全职" in ln:
            nature = "全职"
    for ln in meaningful:
        if any(k in ln for k in CITY_MARKERS):
            city = ln
            break
    return {"source_job_id": card["source_job_id"], "title": title, "nature": nature, "city": city}


async def _fetch_detail_text(page: Any, source: dict[str, Any], job_id: str, timeout_ms: int) -> dict[str, Any]:
    url = _detail_page_url(source, job_id)
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
    except Exception:
        pass
    try:
        await page.wait_for_timeout(3500)
    except Exception:
        pass
    try:
        text = await page.locator("body").inner_text(timeout=5000)
    except Exception:
        text = ""
    description: str | None = None
    requirements: str | None = None
    city_hint: str | None = None
    # City is often present in the header line like "集团|浙江·杭州市|职能类".
    for line in (text or "").splitlines():
        line = line.strip()
        if line and any(k in line for k in CITY_MARKERS) and "|" in line:
            city_hint = line
            break
    if "职位描述" in text:
        tail = text.split("职位描述", 1)[1]
        block = tail.split("职位信息", 1)[0] if "职位信息" in tail else tail
        # Moka portals use "任职要求" (Kingsoft) or "职位要求" (Geely).
        for req_title in ("任职要求", "职位要求"):
            if req_title in block:
                desc_part, req_part = block.split(req_title, 1)
                description = _norm(desc_part) or None
                requirements = _norm(req_part) or None
                break
        else:
            description = _norm(block) or None
    return {"description": description, "requirements": requirements, "city_hint": city_hint}


class MokaAdapter:
    """Adapter for Moka-powered campus recruitment portals (browser-driven)."""

    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        max_jobs = min(max(int(source.get("max_jobs", 30)), 1), 100)
        max_detail = min(max(int(source.get("max_detail", 30)), 1), 60)
        timeout_ms = int(os.getenv("CRAWL_TIMEOUT_MS", "60000"))
        browser = None
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    locale="zh-CN",
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/126.0 Safari/537.36"
                    ),
                )
                page = await context.new_page()
                list_url = _list_url(source)
                try:
                    await page.goto(list_url, wait_until="domcontentloaded", timeout=timeout_ms)
                except Exception:
                    pass
                try:
                    await page.wait_for_timeout(5000)
                except Exception:
                    pass
                cards, blocked = await _collect_cards(page, timeout_ms)
                if blocked:
                    return CollectionResult([], False, [list_url], blocked)
                cards = cards[:max_jobs]
                items: list[ListingItem] = []
                for idx, card in enumerate(cards):
                    raw = _parse_card(card)
                    if idx < max_detail:
                        # Guard each detail fetch with a hard wall-clock bound so a
                        # single slow/hung detail page cannot stall the whole run.
                        try:
                            detail = await asyncio.wait_for(
                                _fetch_detail_text(page, source, card["source_job_id"], timeout_ms),
                                timeout=30,
                            )
                        except Exception:
                            detail = {}
                        raw.update(detail)
                    detail_url = _detail_page_url(source, card["source_job_id"])
                    items.append(ListingItem(card["source_job_id"], raw["title"], detail_url, raw))
                return CollectionResult(items, False, [list_url])
        finally:
            if browser is not None:
                try:
                    await browser.close()
                except Exception:
                    pass

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        # Details were pre-fetched during listing while the browser was open.
        return item.raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        return normalize_moka_job(raw, source)


def _normalize_moka_city(value: str | None) -> str | None:
    """Normalize Moka city strings like '北京市' / '广东·珠海市' to '北京' / '珠海'."""
    if not value:
        return None
    cities: list[str] = []
    for part in re.split(r"[/|,，、;；]+", value):
        part = part.strip()
        if not part:
            continue
        norm = normalize_location_name(part)
        if norm and norm not in cities:
            cities.append(norm)
    return " / ".join(cities) or None


def normalize_moka_job(raw: dict[str, Any], source: dict[str, Any]) -> dict[str, Any] | None:
    job_id = str(raw.get("source_job_id") or "").strip()
    title = str(raw.get("title") or "").strip()
    description = str(raw.get("description") or "").strip()
    requirements = str(raw.get("requirements") or "").strip()
    if not job_id or not title:
        return None
    nature = normalize_job_nature(str(raw.get("nature") or "全职"), title, description + " " + requirements)
    if nature is None:
        nature = "全职"
    city = raw.get("city") or None
    if not city:
        hint = raw.get("city_hint") or ""
        city = next((ln for ln in hint.split("|") if any(k in ln for k in CITY_MARKERS)), None)
    canonical = {
        "company": source["company"],
        "title": title[:160],
        "city": _normalize_moka_city(city),
        "job_nature": nature,
        "category": normalize_category(None, title, description + " " + requirements),
        "degree": normalize_degree(None, requirements),
        "graduate_year": None,
        "requirements": requirements or None,
        "description": description or None,
        # Official campus detail route is the application entry.
        "apply_url": _detail_page_url(source, job_id),
        "source_url": source["url"],
        "source_job_id": job_id,
        "published_at": None,
    }
    digest = "|".join(str(canonical.get(k) or "") for k in (
        "company", "title", "city", "job_nature", "source_job_id", "apply_url",
    ))
    canonical["content_hash"] = hashlib.sha256(digest.encode("utf-8", "ignore")).hexdigest()
    canonical["source_id"] = source["id"]
    canonical["raw"] = raw
    return canonical


__all__ = ["MokaAdapter", "normalize_moka_job"]
