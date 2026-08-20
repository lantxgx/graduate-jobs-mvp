"""Public China Construction Bank campus-job API adapter.

The site exposes listing/detail JSON through the same public endpoints used by
its normal job pages.  We intentionally keep this adapter bounded and do not
attempt login-only application calls.
"""
from __future__ import annotations

import hashlib
from typing import Any
from urllib.parse import urlsplit

import httpx

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_category, normalize_city, normalize_degree, normalize_job_nature, normalize_job


class CcbCampusAdapter:
    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        p = urlsplit(source["url"])
        endpoint = f"{p.scheme}://{p.netloc}/tran/WCCMainPlatV5"
        common = {"CCB_IBSVersion": "V5", "isAjaxRequest": "true", "SERVLET_NAME": "WCCMainPlatV5"}
        headers = {"User-Agent": "Mozilla/5.0", "Referer": source["url"]}
        max_jobs = min(max(int(source.get("max_jobs", 10)), 1), 20)
        async with httpx.AsyncClient(timeout=30, verify=False, headers=headers) as client:
            params = common | {"TXCODE": "NHR104", "planType": "XY", "PAGE_JUMP": "1", "PAGE_SIZE": str(max_jobs)}
            response = await client.get(endpoint, params=params)
            if response.status_code in (403, 429):
                return CollectionResult([], False, [str(response.url)], f"http_{response.status_code}")
            response.raise_for_status()
            payload = response.json()
        rows = payload.get("planPostList") if isinstance(payload, dict) else None
        if not isinstance(rows, list) or not rows:
            return CollectionResult([], False, [str(response.url)], "no_concrete_visible_job_cards")
        items = []
        for row in rows[:max_jobs]:
            if not isinstance(row, dict) or not row.get("planPost"):
                continue
            detail_url = f"{p.scheme}://{p.netloc}/cn/job/job_detail.html?planType=XY&planId={row.get('planId','')}&planPost={row['planPost']}&orgId={row.get('orgId','')}&secondOrgId={row.get('secondOrgId','')}"
            items.append(ListingItem(str(row["planPost"]), str(row.get("planPostName") or ""), detail_url, row))
        return CollectionResult(items, False, [str(response.url)])

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        p = urlsplit(source["url"])
        endpoint = f"{p.scheme}://{p.netloc}/tran/WCCMainPlatV5"
        row = item.raw
        params = {"CCB_IBSVersion": "V5", "isAjaxRequest": "true", "SERVLET_NAME": "WCCMainPlatV5", "TXCODE": "NHR107", "planId": row.get("planId", ""), "planPost": row.get("planPost", ""), "planType": "XY", "orgId": row.get("secondOrgId", "")}
        async with httpx.AsyncClient(timeout=30, verify=False, headers={"User-Agent": "Mozilla/5.0", "Referer": item.detail_url}) as client:
            response = await client.get(endpoint, params=params)
            if response.status_code in (403, 429):
                return {"_error": f"http_{response.status_code}"}
            response.raise_for_status()
            try:
                detail = response.json()
            except ValueError:
                return {"_error": "invalid_json"}
        if not isinstance(detail, dict) or detail.get("SUCCESS") == "false":
            return {"_error": "detail_unavailable", "listing": row}
        return detail | {"listing": row}

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        if raw.get("_error"):
            return None
        row = raw.get("detail") if isinstance(raw.get("detail"), dict) else raw
        listing = raw.get("listing") if isinstance(raw.get("listing"), dict) else {}
        title = row.get("planPostName") or listing.get("planPostName")
        desc = row.get("postDescription") or row.get("jobDescription") or row.get("description") or row.get("duty")
        req = row.get("postRequirement") or row.get("jobRequirement") or row.get("requirements")
        city = row.get("workPlace") or listing.get("workPlace")
        nature = normalize_job_nature("校园招聘", str(title or ""), str(desc or "") + str(req or ""))
        if not title or not (desc or req) or not nature:
            return None
        item = {"company": source["company"], "title": str(title), "city": normalize_city(city), "job_nature": nature,
                "category": normalize_category("", str(title), str(desc or "")), "degree": normalize_degree(row.get("education"), str(req or "")),
                "description": desc, "requirements": req, "apply_url": source["url"], "source_url": source["url"],
                "source_job_id": str(listing.get("planPost") or row.get("planPost") or ""), "published_at": row.get("postDate") or listing.get("postDate")}
        digest = "|".join(str(item.get(k) or "") for k in ("company", "title", "city", "job_nature", "source_job_id", "apply_url", "description", "requirements"))
        item["content_hash"] = hashlib.sha256(digest.encode()).hexdigest()
        item["source_id"] = source["id"]
        item["raw"] = raw
        return normalize_job(item, source)


__all__ = ["CcbCampusAdapter"]
