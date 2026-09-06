"""Public NetEase ThunderFire campus recruitment API adapter."""
from __future__ import annotations

import hashlib
import json
from typing import Any

from playwright.async_api import async_playwright

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_job


LIST_ENDPOINT = "https://xiaozhao.leihuo.netease.com/api/apply/job/list/show"
DETAIL_ENDPOINT = "https://xiaozhao.leihuo.netease.com/api/apply/job/detail/show"


class LeihuoCampusAdapter:
    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        limit = min(max(int(source.get("max_jobs", 10)), 1), 20)
        project_id = str(source.get("project_id", "77"))
        params = {
            "job_name": "",
            "page_size": str(limit),
            "page_number": "1",
            "project_id": project_id,
        }
        async with async_playwright() as pw:
            request = await pw.request.new_context(
                extra_http_headers={"User-Agent": "Mozilla/5.0", "Referer": source["url"]},
                timeout=30000,
            )
            try:
                response = await request.get(LIST_ENDPOINT, params=params)
                if response.status in (403, 429):
                    return CollectionResult([], False, [LIST_ENDPOINT], f"http_{response.status}")
                body = json.loads((await response.body()).decode("utf-8"))
            finally:
                await request.dispose()
        data = body.get("data") if isinstance(body, dict) else None
        rows = data.get("apply_job_list") if isinstance(data, dict) else None
        if not isinstance(rows, list):
            return CollectionResult([], False, [LIST_ENDPOINT], "no_public_position_payload")
        items = [
            ListingItem(
                str(row["ehr_job_id"]),
                str(row.get("job_name") or ""),
                str(row.get("job_detail_url") or ""),
                row,
            )
            for row in rows[:limit]
            if isinstance(row, dict) and row.get("ehr_job_id") and row.get("job_name")
        ]
        if not items:
            return CollectionResult([], False, [LIST_ENDPOINT], "no_concrete_visible_job_cards")
        # This is an intentional bounded sample, not a collection failure.
        # Keep snapshot_complete=false without populating the runner's
        # failure-oriented stop_reason field.
        return CollectionResult(items, False, [LIST_ENDPOINT])

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        project_id = str(source.get("project_id", "77"))
        async with async_playwright() as pw:
            request = await pw.request.new_context(
                extra_http_headers={"User-Agent": "Mozilla/5.0", "Referer": source["url"]},
                timeout=30000,
            )
            try:
                response = await request.get(
                    DETAIL_ENDPOINT,
                    params={"job_id": item.source_job_id, "project_id": project_id},
                )
                if response.status in (403, 429):
                    return {}
                body = json.loads((await response.body()).decode("utf-8"))
            finally:
                await request.dispose()
        detail = body.get("data") if isinstance(body, dict) else None
        if not isinstance(detail, dict):
            return {}
        merged = dict(item.raw)
        merged.update(detail)
        return merged

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        title = str(raw.get("job_name") or "").strip()
        description = str(raw.get("job_description") or "").strip()
        requirements = str(raw.get("job_requirement") or "").strip()
        city = str(raw.get("work_place_name") or "").strip()
        apply_url = str(raw.get("job_detail_url") or "").strip()
        if not title or not description or not requirements or not city or not apply_url:
            return None
        canonical = normalize_job(
            {
                "id": str(raw.get("ehr_job_id") or raw.get("job_code") or ""),
                "title": title,
                "job_type": raw.get("type_name") or "",
                "category": raw.get("category_name") or "",
                "workplace": city,
                "degree": requirements,
                "description": description,
                "requirements": requirements,
                "apply_url": apply_url,
                "published_at": raw.get("published_at"),
            },
            source,
        )
        if canonical is None:
            return None
        target = str(raw.get("target") or raw.get("job_target") or "")
        for year in ("2026", "2027", "2028"):
            if year in target:
                canonical["graduate_year"] = year
                break
        digest = "|".join(
            str(canonical.get(key) or "")
            for key in ("company", "title", "city", "job_nature", "source_job_id", "apply_url", "description", "requirements")
        )
        canonical["content_hash"] = hashlib.sha256(digest.encode("utf-8", "ignore")).hexdigest()
        return canonical


__all__ = ["LeihuoCampusAdapter"]
