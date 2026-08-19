"""Conservative adapter for Lever's public postings JSON feed."""

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
        for key in ("name", "text", "value", "label"):
            result = _text(value.get(key))
            if result:
                return result
    if isinstance(value, list):
        return " / ".join(result for result in (_text(item) for item in value) if result)
    return str(value or "").strip()


def normalize_lever_job(raw: dict[str, Any], source: dict[str, Any]) -> dict[str, Any] | None:
    source_job_id = _text(raw.get("id") or raw.get("posting_id"))
    title = _text(raw.get("text") or raw.get("title") or raw.get("name"))
    categories = raw.get("categories") if isinstance(raw.get("categories"), dict) else {}
    apply_url = _text(raw.get("applyUrl") or raw.get("apply_url") or raw.get("hostedUrl") or raw.get("hosted_url"))
    if not source_job_id or not title or not apply_url or not apply_url.startswith(("https://", "http://")):
        return None

    description = _text(raw.get("descriptionPlain") or raw.get("description") or raw.get("content"))
    requirements = _text(raw.get("requirements") or raw.get("lists"))
    nature_raw = _text(categories.get("commitment") or raw.get("employment_type") or raw.get("job_type"))
    nature = normalize_job_nature(nature_raw, title, f"{description} {requirements}")
    if nature is None:
        return None

    category_raw = _text(categories.get("department") or categories.get("team") or raw.get("department"))
    canonical = {
        "company": source["company"],
        "title": title[:160],
        "city": normalize_city(_text(categories.get("location") or raw.get("location")) or None),
        "job_nature": nature,
        "category": normalize_category(category_raw, title, f"{title} {category_raw}"),
        "degree": normalize_degree(_text(raw.get("education") or raw.get("degree")), requirements or description),
        "graduate_year": None,
        "requirements": requirements or None,
        "description": description or None,
        "apply_url": apply_url,
        "source_url": source["url"],
        "source_job_id": source_job_id,
        "published_at": _text(raw.get("createdAt") or raw.get("updatedAt") or raw.get("published_at")) or None,
    }
    digest = "|".join(str(canonical.get(key) or "") for key in (
        "company", "title", "city", "job_nature", "source_job_id", "apply_url",
    ))
    canonical["content_hash"] = hashlib.sha256(digest.encode("utf-8", "ignore")).hexdigest()
    canonical["source_id"] = source["id"]
    canonical["raw"] = raw
    return canonical


class LeverAdapter:
    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        site_token = str(source.get("site_token") or "").strip()
        if not site_token:
            return CollectionResult([], False, [], "lever_site_token_missing")
        max_jobs = min(max(int(source.get("max_jobs", 20)), 1), 20)
        endpoint = str(source.get("api_url") or f"https://api.lever.co/v0/postings/{site_token}?mode=json")
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
        if not isinstance(payload, list):
            return CollectionResult([], False, response_urls, "lever_postings_payload_invalid")
        items: list[ListingItem] = []
        for raw in payload[:max_jobs]:
            if not isinstance(raw, dict):
                continue
            item = normalize_lever_job(raw, source)
            if item:
                items.append(ListingItem(item["source_job_id"], item["title"], item["apply_url"], raw))
        return CollectionResult(items, len(payload) <= len(items), response_urls)

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        return item.raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        return normalize_lever_job(raw, source)


__all__ = ["LeverAdapter", "normalize_lever_job"]
