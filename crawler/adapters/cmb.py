"""Public China Merchants Bank campus-job API adapter."""
from __future__ import annotations

import hashlib
import re
from html import unescape
from typing import Any
from urllib.parse import urlsplit

import httpx

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_category, normalize_degree, normalize_job, normalize_job_nature


class CmbCampusAdapter:
    def _headers(self, referer: str) -> dict[str, str]:
        return {
            "User-Agent": "Mozilla/5.0",
            "Referer": referer,
            "Origin": "https://career.cmbchina.com",
            "X-B3-BusinessId": "LZ4101CMBRecruitmentPCFront",
        }

    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        page_size = min(max(int(source.get("max_jobs", 10)), 1), 20)
        recruitment_type = source["recruitment_type_id"]
        endpoint = "https://career.cmbchina.com/api/campusRecruitmentWebsite/job/getList"
        payload = {
            "recruitmentTypeId": recruitment_type,
            "pageIndex": 1,
            "pageSize": page_size,
            "orgIdList": [],
            "locationIdList": [],
            "jobTypeIdList": [],
            "keywords": "",
        }
        async with httpx.AsyncClient(timeout=30, headers=self._headers(source["url"])) as client:
            response = await client.post(endpoint, json=payload)
            if response.status_code in (403, 429):
                return CollectionResult([], False, [str(response.url)], f"http_{response.status_code}")
            response.raise_for_status()
            result = response.json()
        body = result.get("body") if isinstance(result, dict) else None
        rows = body.get("data") if isinstance(body, dict) else None
        if result.get("returnCode") != "SUC0000" or not isinstance(rows, list):
            return CollectionResult([], False, [endpoint], "no_concrete_visible_job_cards")
        items = []
        for row in rows[:page_size]:
            if not isinstance(row, dict) or not row.get("publishGID") or not row.get("jobDisplay"):
                continue
            gid = str(row["publishGID"])
            detail_url = f"https://career.cmbchina.com/positionDetail/{recruitment_type}?publishId={gid}"
            items.append(ListingItem(gid, str(row["jobDisplay"]), detail_url, row))
        return CollectionResult(items, False, [endpoint])

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        endpoint = "https://career.cmbchina.com/api/campusRecruitmentWebsite/job/getDetail"
        async with httpx.AsyncClient(timeout=30, headers=self._headers(item.detail_url)) as client:
            response = await client.get(endpoint, params={"publishId": item.source_job_id})
            if response.status_code in (403, 429):
                return {"_error": f"http_{response.status_code}", "listing": item.raw}
            response.raise_for_status()
            result = response.json()
        body = result.get("body") if isinstance(result, dict) else None
        if result.get("returnCode") != "SUC0000" or not isinstance(body, dict):
            return {"_error": "detail_unavailable", "listing": item.raw}
        return {"detail": body, "listing": item.raw}

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        if raw.get("_error"):
            return None
        detail = raw.get("detail") or {}
        listing = raw.get("listing") or {}
        title = str(detail.get("jobDisplay") or listing.get("jobDisplay") or "").strip()
        description = self._clean_html(detail.get("jobResponsibility"))
        requirements = self._clean_html(detail.get("jobRequirement"))
        if not title or not (description or requirements):
            return None
        job = {
            "company": source["company"],
            "title": title,
            "city": str(detail.get("locationName") or listing.get("locationName") or ""),
            "job_nature": normalize_job_nature("实习" if "实习" in title or "实习" in requirements else "校园招聘", title, description),
            "category": normalize_category("", title, description),
            "degree": normalize_degree("", requirements),
            "description": description,
            "requirements": requirements,
            "apply_url": raw.get("detail_url") or f"https://career.cmbchina.com/positionDetail/{source['recruitment_type_id']}?publishId={listing.get('publishGID', '')}",
            "source_url": source["url"],
            "source_job_id": str(detail.get("publishGID") or listing.get("publishGID") or ""),
            "published_at": None,
        }
        digest = "|".join(str(job.get(k) or "") for k in ("company", "title", "city", "source_job_id", "description", "requirements"))
        job["content_hash"] = hashlib.sha256(digest.encode("utf-8", "ignore")).hexdigest()
        job["source_id"] = source["id"]
        job["raw"] = raw
        return normalize_job(job, source)

    @staticmethod
    def _clean_html(value: Any) -> str:
        text = unescape(str(value or ""))
        text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
        text = re.sub(r"<[^>]+>", "", text)
        return re.sub(r"\n{3,}", "\n\n", text).strip()


__all__ = ["CmbCampusAdapter"]
