"""Pinduoduo (PDD) official campus recruitment adapter.

The PDD campus portal exposes a clean public JSON API on
careers.pddglobalhr.com:

- List:   POST /api/careers/api/recruit/position/list
          body {"page": N, "pageSize": 10, "t": null}
          -> result.total (in-scope count), result.list[] rows.
- Detail: POST /api/careers/api/recruit/position/detail
          body {"id": "<positionGuid>"}
          -> result.serveRequirement (requirements) + result.jobDuty.

The list exposes a stable position GUID, title, work location, category,
description and graduate year. The official application entry is the public
campus list page (https://careers.pddglobalhr.com/campus/grad); the public
payload does not expose a per-job apply URL, so the campus list URL is used as
the apply entry, matching the Meituan precedent. The source is therefore
integrated but snapshot_complete=false.
"""

from __future__ import annotations

import hashlib
from typing import Any

import httpx

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import (
    JOB_NATURE_FULL_TIME,
    normalize_category,
    normalize_city,
    normalize_degree,
    normalize_job_nature,
)

LIST_URL = "https://careers.pddglobalhr.com/api/careers/api/recruit/position/list"
DETAIL_URL = "https://careers.pddglobalhr.com/api/careers/api/recruit/position/detail"
PAGE_SIZE = 10


def _request_headers(source: dict[str, Any]) -> dict[str, str]:
    return {"Content-Type": "application/json", "Referer": source["url"]}


def normalize_pdd_job(raw: dict[str, Any], source: dict[str, Any]) -> dict[str, Any] | None:
    job_id = str(raw.get("id") or "").strip()
    title = str(raw.get("name") or "").strip()
    description = str(raw.get("jobDuty") or "").strip()
    requirements = str(raw.get("serveRequirement") or "").strip()
    if not job_id or not title:
        return None
    combined = f"{title} {requirements} {description}"
    nature = normalize_job_nature("", title, combined)
    if nature is None:
        nature = JOB_NATURE_FULL_TIME
    canonical = {
        "company": source["company"],
        "title": title[:160],
        "city": normalize_city(str(raw.get("workLocationName") or "").strip() or None),
        "job_nature": nature,
        "category": normalize_category(raw.get("jobName") or raw.get("job"), title, combined),
        "degree": normalize_degree(None, requirements),
        "graduate_year": str(raw.get("graduationYear") or "").strip() or None,
        "requirements": requirements or None,
        "description": description or None,
        # No per-job apply URL in the public payload; the campus list page is
        # the official application entry (Meituan precedent).
        "apply_url": source["url"],
        "source_url": source["url"],
        "source_job_id": job_id,
        "published_at": None,
    }
    digest = "|".join(str(canonical.get(k) or "") for k in (
        "company", "title", "city", "job_nature", "source_job_id", "apply_url",
    ))
    canonical["content_hash"] = hashlib.sha256(digest.encode("utf-8", "ignore")).hexdigest()
    canonical["source_id"] = source["id"]
    canonical["raw"] = raw
    return canonical


class PddAdapter:
    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        items: list[ListingItem] = []
        response_urls: list[str] = []
        stop_reason: str | None = None
        max_pages = min(max(int(source.get("max_pages", 50)), 1), 50)
        seen: set[str] = set()
        reported_total: int | None = None
        async with httpx.AsyncClient(timeout=30) as client:
            page = 1
            while True:
                if page > max_pages:
                    stop_reason = "pdd_page_limit"
                    break
                try:
                    resp = await client.post(
                        LIST_URL,
                        json={"page": page, "pageSize": PAGE_SIZE, "t": None},
                        headers=_request_headers(source),
                    )
                except Exception:
                    stop_reason = "public_job_page_request_failed"
                    break
                response_urls.append(str(resp.url))
                if resp.status_code in {403, 429}:
                    stop_reason = f"http_{resp.status_code}"
                    break
                if resp.status_code != 200:
                    stop_reason = f"http_{resp.status_code}"
                    break
                try:
                    payload = resp.json()
                except Exception:
                    stop_reason = "public_job_list_invalid_json"
                    break
                result = (payload or {}).get("result") or {}
                if reported_total is None:
                    reported_total = int(result.get("total") or 0)
                rows = result.get("list") or []
                before = len(seen)
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    rid = str(row.get("id") or "").strip()
                    if not rid:
                        continue
                    if rid not in seen:
                        seen.add(rid)
                        items.append(ListingItem(rid, str(row.get("name") or ""), source["url"], row))
                if not rows:
                    break
                if len(seen) >= reported_total and reported_total > 0:
                    break
                if len(seen) == before:
                    stop_reason = "pdd_repeated_page"
                    break
                page += 1
        return CollectionResult(items, False, response_urls, stop_reason)

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        raw = dict(item.raw)
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    DETAIL_URL,
                    json={"id": item.source_job_id},
                    headers=_request_headers(source),
                )
                if resp.status_code == 200:
                    detail = (resp.json() or {}).get("result") or {}
                    if isinstance(detail, dict):
                        raw.update(detail)
        except Exception:
            pass
        return raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        return normalize_pdd_job(raw, source)


__all__ = ["PddAdapter", "normalize_pdd_job"]
