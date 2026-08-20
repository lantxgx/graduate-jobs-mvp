"""Public Huya campus API adapter."""
from __future__ import annotations

from typing import Any
import httpx

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_job


class HuyaCampusAdapter:
    endpoint = "https://api.mokahr.com/v1/jobs/huya"

    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        headers = {"User-Agent": "Mozilla/5.0", "Referer": source["url"], "Origin": "https://hr.huya.com"}
        params = {"mode": "campus", "limit": min(int(source.get("max_jobs", 20)), 100), "offset": 0, "commitment": 1}
        async with httpx.AsyncClient(timeout=30, headers=headers) as client:
            response = await client.get(self.endpoint, params=params)
            if response.status_code in (403, 429):
                return CollectionResult([], False, [str(response.url)], f"http_{response.status_code}")
            response.raise_for_status()
            payload = response.json()
        rows = payload.get("jobs") if isinstance(payload, dict) else None
        if not isinstance(rows, list) or not rows:
            return CollectionResult([], False, [self.endpoint], "no_concrete_visible_job_cards")
        items = []
        for row in rows:
            job_id = str(row.get("id") or "").strip()
            title = str(row.get("title") or "").strip()
            if job_id and title:
                items.append(ListingItem(job_id, title, f"https://hr.huya.com/campus_apply/huya/4112#/job/{job_id}", row))
        return CollectionResult(items, False, [str(response.url)])

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        return item.raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        row = dict(raw)
        row["city"] = " / ".join(str(x.get("city") or x.get("province") or "") for x in (row.get("locations") or []) if isinstance(x, dict))
        row["job_nature"] = row.get("commitment") or "全职"
        row["category"] = (row.get("zhineng") or {}).get("name") if isinstance(row.get("zhineng"), dict) else None
        row["degree"] = row.get("education")
        row["requirements"] = row.get("description")
        row["description"] = row.get("description")
        row["apply_url"] = f"https://hr.huya.com/campus_apply/huya/4112#/job/{row.get('id')}"
        row["source_job_id"] = str(row.get("id") or "")
        row["published_at"] = row.get("publishedAt")
        return normalize_job(row, source)


__all__ = ["HuyaCampusAdapter"]
