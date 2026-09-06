"""Public G-bits campus recruitment API adapter."""
from __future__ import annotations

import hashlib
import json
from typing import Any

from playwright.async_api import async_playwright

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_job


ENDPOINT = "https://joinserver.g-bits.com:8666/humanResource/recruitmentExtranet/ExtrannetCampusPost/queryRecuitPost"


class GbitsCampusAdapter:
    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        limit = min(max(int(source.get("max_jobs", 20)), 1), 20)
        payload = {"currentPage": 1, "pageSize": limit, "recruitsType": "CAMPUS_RECRUITING"}
        async with async_playwright() as pw:
            request = await pw.request.new_context(
                extra_http_headers={"User-Agent": "Mozilla/5.0", "Referer": source["url"]},
                timeout=30000,
            )
            try:
                response = await request.post(ENDPOINT, data=payload)
                if response.status in (403, 429):
                    return CollectionResult([], False, [ENDPOINT], f"http_{response.status}")
                body = json.loads((await response.body()).decode("utf-8"))
            finally:
                await request.dispose()
        rows = ((body.get("data") or {}).get("list") if isinstance(body, dict) else None) or []
        items = [
            ListingItem(str(row["id"]), str(row.get("postName") or ""), source["url"], row)
            for row in rows[:limit]
            if isinstance(row, dict) and row.get("id") and row.get("postName")
        ]
        return CollectionResult(items, False, [ENDPOINT])

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        return item.raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        title = str(raw.get("postName") or "").strip()
        full_text = str(raw.get("description") or "").strip()
        if not title or not full_text:
            return None
        requirements = full_text
        description = full_text
        for marker in ("任职资格", "职位要求", "岗位要求"):
            if marker in full_text:
                description, requirements = full_text.split(marker, 1)
                requirements = marker + requirements
                break
        city = (raw.get("workCity") or {}).get("desc") or raw.get("workAddress") or ""
        canonical = normalize_job(
            {
                "id": str(raw.get("id")),
                "title": title,
                "job_type": raw.get("recruitmentType") or "校园招聘",
                "category": raw.get("postType") or raw.get("rootPostType") or "",
                "workplace": city,
                "degree": requirements,
                "description": description.strip(),
                "requirements": requirements.strip(),
                "apply_url": source["url"],
                "updated_at": raw.get("updateTime"),
            },
            source,
        )
        if canonical is None:
            return None
        digest = "|".join(str(canonical.get(key) or "") for key in ("company", "title", "city", "job_nature", "source_job_id", "apply_url", "description", "requirements"))
        canonical["content_hash"] = hashlib.sha256(digest.encode("utf-8", "ignore")).hexdigest()
        return canonical


__all__ = ["GbitsCampusAdapter"]
