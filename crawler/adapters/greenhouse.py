"""Conservative adapter for Greenhouse's documented public jobs feed.

The feed is useful for companies that publish a public Greenhouse board.  It
is only enabled when the source registry contains a verified ``board_token``
and the returned item already contains an explicit ``absolute_url``.  The
adapter never constructs a detail URL from an ID and does not treat a board
listing as official until the source registry has verified the company
ownership.
"""

from __future__ import annotations

import hashlib
import html
import re
from typing import Any

from playwright.async_api import async_playwright

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_category, normalize_city, normalize_degree, normalize_job_nature


BLOCKED_MARKERS = ("captcha", "验证码", "security verification", "安全验证")


def _text(value: Any) -> str:
    if isinstance(value, str):
        value = re.sub(r"<[^>]+>", " ", value)
        return re.sub(r"\s+", " ", html.unescape(value)).strip()
    if isinstance(value, dict):
        for key in ("name", "title", "value"):
            result = _text(value.get(key))
            if result:
                return result
    if isinstance(value, list):
        return " / ".join(result for result in (_text(item) for item in value) if result)
    return str(value or "").strip()


def _location(raw: dict[str, Any]) -> str | None:
    location = raw.get("location")
    value = _text(location) or _text(raw.get("office")) or _text(raw.get("city"))
    parts = [part.strip() for part in re.split(r"[,，]", value) if part.strip()]
    if len(parts) > 1 and parts[-1].lower() in {"china", "中国", "mainland china"}:
        value = parts[0]
    return normalize_city(value or None)


def normalize_greenhouse_job(raw: dict[str, Any], source: dict[str, Any]) -> dict[str, Any] | None:
    source_job_id = _text(raw.get("id") or raw.get("job_id"))
    title = _text(raw.get("title") or raw.get("name"))
    apply_url = _text(raw.get("absolute_url") or raw.get("apply_url") or raw.get("detail_url"))
    if not source_job_id or not title or not apply_url or not apply_url.startswith(("https://", "http://")):
        return None

    description = _text(raw.get("content") or raw.get("description") or raw.get("job_description"))
    requirements = _text(raw.get("requirements") or raw.get("qualifications"))
    nature_raw = _text(raw.get("employment_type") or raw.get("job_type") or raw.get("recruitment_type"))
    nature = normalize_job_nature(nature_raw, title, f"{description} {requirements}")
    if nature is None:
        return None

    department = _text(raw.get("departments") or raw.get("department") or raw.get("category"))
    category = normalize_category(department, title, f"{title} {department}")
    canonical = {
        "company": source["company"],
        "title": title[:160],
        "city": _location(raw),
        "job_nature": nature,
        "category": category,
        "degree": normalize_degree(_text(raw.get("education") or raw.get("degree")), requirements or description),
        "graduate_year": None,
        "requirements": requirements or None,
        "description": description or None,
        "apply_url": apply_url,
        "source_url": source["url"],
        "source_job_id": source_job_id,
        "published_at": _text(raw.get("updated_at") or raw.get("published_at")) or None,
    }
    digest = "|".join(str(canonical.get(key) or "") for key in (
        "company", "title", "city", "job_nature", "source_job_id", "apply_url",
    ))
    canonical["content_hash"] = hashlib.sha256(digest.encode("utf-8", "ignore")).hexdigest()
    canonical["source_id"] = source["id"]
    canonical["raw"] = raw
    return canonical


class GreenhouseAdapter:
    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        token = str(source.get("board_token") or "").strip()
        if not token:
            return CollectionResult([], False, [], "greenhouse_board_token_missing")
        max_jobs = min(max(int(source.get("max_jobs", 20)), 1), 20)
        endpoint = str(source.get("api_url") or f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true")
        response_urls = [endpoint]
        payload: Any = None
        stop_reason: str | None = None
        async with async_playwright() as playwright:
            request = await playwright.request.new_context()
            try:
                response = await request.get(endpoint, timeout=int(source.get("timeout_ms", 30000)))
                if response.status in {403, 429}:
                    stop_reason = f"http_{response.status}"
                elif response.status != 200:
                    stop_reason = f"http_{response.status}"
                else:
                    body = await response.text()
                    if any(marker.lower() in body.lower() for marker in BLOCKED_MARKERS):
                        stop_reason = "verification_page_detected"
                    else:
                        payload = await response.json()
            finally:
                await request.dispose()
        if stop_reason:
            return CollectionResult([], False, response_urls, stop_reason)
        records = payload.get("jobs") if isinstance(payload, dict) else payload
        if not isinstance(records, list):
            return CollectionResult([], False, response_urls, "greenhouse_jobs_payload_invalid")
        items: list[ListingItem] = []
        for raw in records[:max_jobs]:
            if not isinstance(raw, dict):
                continue
            item = normalize_greenhouse_job(raw, source)
            if item:
                items.append(ListingItem(item["source_job_id"], item["title"], item["apply_url"], raw))
        total = int(payload.get("meta", {}).get("total", len(records))) if isinstance(payload, dict) and isinstance(payload.get("meta"), dict) else len(records)
        return CollectionResult(items, total <= len(items), response_urls)

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        return item.raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        return normalize_greenhouse_job(raw, source)


__all__ = ["GreenhouseAdapter", "normalize_greenhouse_job"]
