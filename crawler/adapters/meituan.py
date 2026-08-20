"""Meituan official campus listing adapter (bounded public page sample)."""
from __future__ import annotations

import hashlib
from typing import Any

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.browser_discovery import discover_job_json
from crawler.normalize import normalize_category, normalize_city, normalize_degree, JOB_NATURE_FULL_TIME, JOB_NATURE_INTERNSHIP


def normalize_meituan_job(raw: dict[str, Any], source: dict[str, Any]) -> dict[str, Any] | None:
    job_id = str(raw.get("jobUnionId") or "").strip()
    title = str(raw.get("name") or "").strip()
    duty = str(raw.get("jobDuty") or raw.get("desc") or "").strip()
    requirement = str(raw.get("jobRequirement") or "").strip()
    if not job_id or not title or not (duty or requirement):
        return None
    cities = [str(x.get("name") or "").strip() for x in (raw.get("cityList") or []) if isinstance(x, dict) and x.get("name")]
    nature = JOB_NATURE_INTERNSHIP if str(raw.get("jobType") or "") in {"2", "intern", "internship"} else JOB_NATURE_FULL_TIME
    canonical = {
        "company": source["company"], "title": title[:160], "city": normalize_city(" / ".join(cities) or None),
        "job_nature": nature,
        "category": normalize_category(raw.get("jobFamily") or raw.get("jobFamilyGroup"), title, duty + " " + requirement),
        "degree": normalize_degree(None, requirement), "graduate_year": None,
        "requirements": requirement or None, "description": duty or None,
        # The public campus page is the official application entry; the API
        # does not expose a per-job URL in its public payload.
        "apply_url": source["url"], "source_url": source["url"], "source_job_id": job_id,
        "published_at": str(raw.get("refreshTime") or "") or None,
    }
    digest = "|".join(str(canonical.get(k) or "") for k in ("company", "title", "city", "job_nature", "source_job_id", "apply_url"))
    canonical["content_hash"] = hashlib.sha256(digest.encode("utf-8")).hexdigest()
    canonical["source_id"] = source["id"]
    canonical["raw"] = raw
    return canonical


class MeituanAdapter:
    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        raw_jobs, urls = await discover_job_json(source["url"])
        jobs = [x for x in raw_jobs if isinstance(x, dict) and x.get("jobUnionId")]
        max_jobs = min(max(int(source.get("max_jobs", 20)), 1), 20)
        jobs = jobs[:max_jobs]
        items = [ListingItem(str(x["jobUnionId"]), str(x.get("name") or ""), source["url"], x) for x in jobs]
        return CollectionResult(items, False, urls)

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        return item.raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        return normalize_meituan_job(raw, source)


__all__ = ["MeituanAdapter", "normalize_meituan_job"]
