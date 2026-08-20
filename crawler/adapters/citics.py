"""Public CITIC Securities campus recruitment API adapter."""
from __future__ import annotations

import hashlib
from typing import Any
from urllib.parse import urlsplit

import httpx

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_category, normalize_city, normalize_degree, normalize_job, normalize_job_nature


class CiticsCampusAdapter:
    endpoint = "https://global-kong.citics.com/api/v1/recruit"

    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        max_jobs = min(max(int(source.get("max_jobs", 20)), 1), 20)
        payload = {"sysNo": "CSE001", "recruitType": "08", "deptype": "Headquarter", "practice": 1, "pageSize": max_jobs, "pageNo": 1}
        headers = {"User-Agent": "Mozilla/5.0", "Referer": source["url"], "Accept-Language": "zh"}
        async with httpx.AsyncClient(timeout=30, verify=False, headers=headers) as client:
            response = await client.post(self.endpoint + "/getPositionList", data=payload)
            if response.status_code in (403, 429):
                return CollectionResult([], False, [str(response.url)], f"http_{response.status_code}")
            response.raise_for_status()
            body = response.json()
        rows = body.get("positionList") if isinstance(body, dict) else None
        if not isinstance(rows, list) or not rows:
            return CollectionResult([], False, [str(response.url)], "no_concrete_visible_job_cards")
        items = []
        for row in rows[:max_jobs]:
            if not isinstance(row, dict) or not row.get("positionNo"):
                continue
            detail = f"https://careers.citics.com/positonDetailHeadquarters?deptNo={row.get('deptNo','')}&positionNo={row['positionNo']}&pageName=headquarters&resumeType=0"
            items.append(ListingItem(str(row["positionNo"]), str(row.get("positionName") or ""), detail, row))
        return CollectionResult(items, int(body.get("count") or len(items)) <= len(items), [str(response.url)])

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        row = item.raw
        payload = {"sysNo": "CSE001", "deptNo": row.get("deptNo", ""), "positionNo": row.get("positionNo", ""), "recruitType": "08"}
        headers = {"User-Agent": "Mozilla/5.0", "Referer": item.detail_url, "Accept-Language": "zh"}
        async with httpx.AsyncClient(timeout=30, verify=False, headers=headers) as client:
            response = await client.post(self.endpoint + "/getPositionInfo", data=payload)
            if response.status_code in (403, 429):
                return {"_error": f"http_{response.status_code}", "listing": row}
            response.raise_for_status()
            body = response.json()
        info = body.get("positionInfo") if isinstance(body, dict) else None
        return {"detail": info, "listing": row} if isinstance(info, dict) else {"_error": "detail_unavailable", "listing": row}

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        if raw.get("_error") or not isinstance(raw.get("detail"), dict):
            return None
        row = raw["detail"]
        title = str(row.get("positionName") or "").strip()
        desc = str(row.get("positionDesc") or "").strip()
        req = str(row.get("qualification") or "").strip()
        nature = normalize_job_nature(str(row.get("type") or "校园招聘"), title, desc + req)
        if not title or not (desc or req) or not nature:
            return None
        listing = raw.get("listing") or {}
        item = {"company": source["company"], "title": title, "city": normalize_city(row.get("workplace") or listing.get("workplace")),
                "job_nature": nature, "category": normalize_category("", title, desc), "degree": normalize_degree("", req),
                "description": desc, "requirements": req, "apply_url": f"https://careers.citics.com/positonDetailHeadquarters?deptNo={row.get('deptNo', listing.get('deptNo',''))}&positionNo={row.get('positionNo', listing.get('positionNo',''))}&pageName=headquarters&resumeType=0",
                "source_url": source["url"], "source_job_id": str(row.get("positionNo") or listing.get("positionNo") or ""), "published_at": None}
        digest = "|".join(str(item.get(k) or "") for k in ("company", "title", "city", "job_nature", "source_job_id", "apply_url", "description", "requirements"))
        item["content_hash"] = hashlib.sha256(digest.encode()).hexdigest(); item["source_id"] = source["id"]; item["raw"] = raw
        return normalize_job(item, source)


__all__ = ["CiticsCampusAdapter"]
