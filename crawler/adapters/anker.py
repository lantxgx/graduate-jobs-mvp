"""Bounded adapter for Anker Innovations' public campus API."""

from __future__ import annotations

import hashlib
import re
from typing import Any

from playwright.async_api import async_playwright

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_category, normalize_degree, normalize_job_nature, normalize_city


API_BASE = "https://rainbowbridge.anker.com"
DEFAULT_WEBSITE_ID = "7268177039772633400"
APPLY_URL = "https://anker-in.jobs.feishu.cn/189381/position/application"


def _name(value: Any) -> str:
    if isinstance(value, dict):
        for key in ("zh_cn", "name", "en_us"):
            if value.get(key):
                return str(value[key]).strip()
    return str(value or "").strip()


def _text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip().strip('"')


def _category(value: str, title: str, description: str) -> str:
    raw = value.lower()
    if any(token in raw for token in ("销售", "品牌", "零售", "gtm", "marketing")):
        return "市场/销售"
    if any(token in raw for token in ("产品", "product")):
        return "产品"
    if any(token in raw for token in ("技术服务", "培训", "人力", "hr")):
        return "职能"
    return normalize_category(value, title, description)


class AnkerCampusAdapter:
    def _url(self, source: dict[str, Any], path: str) -> str:
        website_id = source.get("website_id", DEFAULT_WEBSITE_ID)
        return f"{API_BASE}/api/lark/hire/v1/websites/{website_id}{path}"

    async def _get(self, context: Any, url: str) -> dict[str, Any]:
        response = await context.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status in (403, 429):
            raise RuntimeError(f"http_{response.status}")
        if not response.ok:
            raise RuntimeError(f"http_{response.status}")
        payload = await response.json()
        if not isinstance(payload, dict) or payload.get("code") != 0:
            raise RuntimeError("invalid_public_api_payload")
        return payload

    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        limit = min(max(int(source.get("max_jobs", 10)), 1), 10)
        url = self._url(source, "/job_posts/search?page_size=10&page_token=")
        body = {"job_function_id_list": [], "city_code_list": [], "keyword": "", "job_lang_list": []}
        async with async_playwright() as pw:
            request = await pw.request.new_context(timeout=30000)
            try:
                response = await request.post(url, data=body, headers={"Content-Type": "application/json"})
                if response.status in (403, 429):
                    raise RuntimeError(f"http_{response.status}")
                if not response.ok:
                    raise RuntimeError(f"http_{response.status}")
                payload = await response.json()
            except RuntimeError as exc:
                return CollectionResult([], False, [url], str(exc))
            finally:
                await request.dispose()
        if not isinstance(payload, dict) or payload.get("code") != 0:
            return CollectionResult([], False, [url], "invalid_public_api_payload")
        rows = ((payload.get("data") or {}).get("items") or [])
        items: list[ListingItem] = []
        for row in rows:
            if not isinstance(row, dict) or not row.get("id") or not row.get("title"):
                continue
            subject = _name((row.get("subject") or {}).get("name"))
            if not any(token in subject.lower() for token in ("校招", "校园", "campus", "graduate", "实习")):
                continue
            items.append(ListingItem(str(row["id"]), str(row["title"]), self._url(source, f"/job_posts/{row['id']}"), row))
            if len(items) >= limit:
                break
        if not items:
            return CollectionResult([], False, [url], "no_concrete_public_campus_jobs")
        return CollectionResult(items, False, [url])

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        url = self._url(source, f"/job_posts/{item.source_job_id}")
        async with async_playwright() as pw:
            request = await pw.request.new_context(timeout=30000)
            try:
                payload = await self._get(request, url)
            finally:
                await request.dispose()
        job = ((payload.get("data") or {}).get("job_post") or {})
        return {**item.raw, **job, "source_job_id": item.source_job_id}

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        subject = _name((raw.get("subject") or {}).get("name"))
        title = _text(raw.get("title"))
        description = _text(raw.get("description"))
        requirements = _text(raw.get("requirement"))
        address = raw.get("address") or {}
        city = _name((address.get("city") or {}).get("name"))
        nature = _name((raw.get("job_recruitment_type") or {}).get("name")) + " " + subject
        category = _name((raw.get("job_function") or {}).get("name"))
        job = {
            "company": source["company"], "title": title[:160], "city": normalize_city(city),
            "job_nature": normalize_job_nature(nature, title, description),
            "category": _category(category, title, description),
            "degree": normalize_degree(None, requirements), "graduate_year": re.search(r"20\d{2}", subject + " " + requirements).group(0) if re.search(r"20\d{2}", subject + " " + requirements) else None,
            "requirements": requirements, "description": description, "apply_url": source.get("apply_url", APPLY_URL),
            "source_url": source["url"], "source_job_id": str(raw.get("source_job_id") or raw.get("id") or ""),
            "published_at": raw.get("modify_time"), "source_id": source["id"], "raw": raw,
        }
        if not job["source_job_id"] or not title or not job["city"] or not description or not requirements:
            return None
        digest = "|".join(str(job.get(key) or "") for key in ("company", "title", "city", "job_nature", "category", "degree", "source_job_id", "apply_url", "description", "requirements"))
        job["content_hash"] = hashlib.sha256(digest.encode("utf-8", "ignore")).hexdigest()
        return job


__all__ = ["AnkerCampusAdapter"]
