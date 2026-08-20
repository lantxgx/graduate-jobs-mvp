"""Public campus JSON adapter for Sanqi Interactive Entertainment (37.com)."""
from __future__ import annotations

import hashlib
from typing import Any
import httpx

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_job


class SanqiCampusAdapter:
    endpoint = "https://zhaopin.37.com/index.php"

    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        params = {"m": "Home", "c": "campus", "a": "getIndexPage", "key": "", "post_type": "", "place_type": "", "page": 1}
        async with httpx.AsyncClient(timeout=30, headers={"User-Agent": "Mozilla/5.0", "Referer": source["url"]}) as client:
            response = await client.get(self.endpoint, params=params)
            if response.status_code in (403, 429):
                return CollectionResult([], False, [str(response.url)], f"http_{response.status_code}")
            response.raise_for_status()
            payload = response.json()
        rows = ((payload.get("data") or {}).get("list") if isinstance(payload, dict) else None)
        if not isinstance(rows, list) or not rows:
            return CollectionResult([], False, [str(response.url)], "no_concrete_visible_job_cards")
        max_jobs = min(max(int(source.get("max_jobs", 10)), 1), 20)
        items: list[ListingItem] = []
        for row in rows[:max_jobs]:
            if not isinstance(row, dict) or not row.get("url") or not row.get("name"):
                continue
            job_id = str(row["url"]).split("/job/")[-1].split("#", 1)[0]
            items.append(ListingItem(job_id, str(row["name"]), str(row["url"]), row))
        return CollectionResult(items, False, [str(response.url)])

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        return item.raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        row = dict(raw)
        row["title"] = row.get("name")
        row["city"] = row.get("work_place")
        row["job_nature"] = "全职"
        row["category"] = row.get("pname")
        row["description"] = row.get("duty")
        row["requirements"] = row.get("duty")
        row["apply_url"] = row.get("url")
        row["source_job_id"] = str(row.get("url") or "").split("/job/")[-1].split("#", 1)[0]
        row["degree"] = "未注明"
        return normalize_job(row, source)


__all__ = ["SanqiCampusAdapter"]
