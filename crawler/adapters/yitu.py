"""Public Yitu campus recruitment adapter.

Yitu's official career page loads the campus list from Moka's public
``/v1/jobs/yitu-inc`` endpoint during normal page loading.  The adapter uses
that public response directly, keeps the official Yitu page as ``source_url``,
and does not infer missing fields.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any

import httpx
from bs4 import BeautifulSoup

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_job


class YituCampusAdapter:
    endpoint = "https://api.mokahr.com/v1/jobs/yitu-inc"

    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        limit = min(max(int(source.get("max_jobs", 20)), 1), 1000)
        params = {"mode": "campus", "limit": limit, "offset": 0}
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": source["url"],
            "Origin": "https://www.yitutech.com",
        }
        async with httpx.AsyncClient(timeout=30, headers=headers) as client:
            response = await client.get(self.endpoint, params=params)
            if response.status_code in (403, 429):
                return CollectionResult([], False, [str(response.url)], f"http_{response.status_code}")
            response.raise_for_status()
            payload = response.json()
        rows = payload.get("jobs") if isinstance(payload, dict) else None
        if not isinstance(rows, list) or not rows:
            return CollectionResult([], False, [str(response.url)], "no_concrete_visible_job_cards")
        items: list[ListingItem] = []
        for row in rows:
            if not isinstance(row, dict) or str(row.get("status") or "").lower() == "closed":
                continue
            job_id = str(row.get("id") or "").strip()
            title = str(row.get("title") or "").strip()
            if job_id and title:
                apply_url = f"https://app.mokahr.com/campus_apply/yitu-inc/#/job/{job_id}/apply?pure=1"
                items.append(ListingItem(job_id, title, apply_url, row))
        if not items:
            return CollectionResult([], False, [str(response.url)], "no_concrete_visible_job_cards")
        # The public page filters campus full-time/internship records client-side;
        # keep the bounded response and let normalization enforce the two natures.
        return CollectionResult(items, False, [str(response.url)])

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        return item.raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        row = dict(raw)
        description_html = str(row.get("description") or "").strip()
        text = BeautifulSoup(description_html, "html.parser").get_text("\n", strip=True)
        text = re.sub(r"\n{2,}", "\n", text).strip()
        requirements = ""
        for marker in ("任职资格", "任职要求", "岗位要求", "职位要求", "应聘要求"):
            if marker in text:
                before, after = text.split(marker, 1)
                text, requirements = before.strip(), after.strip()
                break
        if not requirements:
            requirements = text
        locations = row.get("locations") or []
        city_parts = []
        for location in locations:
            if not isinstance(location, dict):
                continue
            # The public payload exposes Shanghai as province plus Xuhui
            # district; keep the city-level value and do not promote a
            # district to a city when the city key is absent.
            city = location.get("city") or location.get("province") or location.get("area")
            if city and str(city) not in city_parts:
                city_parts.append(str(city))
        row.update(
            {
                "city": " / ".join(city_parts),
                "job_nature": row.get("commitment") or "全职",
                "category": (row.get("zhineng") or {}).get("name") if isinstance(row.get("zhineng"), dict) else None,
                "degree": row.get("education"),
                "description": text,
                "requirements": requirements,
                "apply_url": f"https://app.mokahr.com/campus_apply/yitu-inc/#/job/{row.get('id')}/apply?pure=1",
                "source_job_id": str(row.get("id") or ""),
                "published_at": row.get("publishedAt"),
            }
        )
        return normalize_job(row, source)


__all__ = ["YituCampusAdapter"]
