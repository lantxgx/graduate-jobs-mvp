"""Public BYD campus recruitment portal adapter."""
from __future__ import annotations

import hashlib
from typing import Any
from urllib.parse import urlencode, urlsplit, urlunsplit

from playwright.async_api import async_playwright

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_job


LIST_PATH = "/portal/api/portal-api/schoolPortal/queryPositionList"
DETAIL_PATH = "/portal/api/portal-api/schoolPortal/queryPosition"


class BydCampusAdapter:
    def _endpoint(self, source: dict[str, Any], path: str) -> str:
        parsed = urlsplit(source["url"])
        return urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))

    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        max_jobs = min(max(int(source.get("max_jobs", 20)), 1), 20)
        headers = {"User-Agent": "Mozilla/5.0", "Referer": source["url"]}
        channels = source.get("channels") or [{"campus_nature": "008501", "job_nature": "全职"}]
        response_urls = []
        items: list[ListingItem] = []
        async with async_playwright() as pw:
            client = await pw.request.new_context(extra_http_headers=headers, timeout=30000)
            try:
                for channel in channels:
                    if len(items) >= max_jobs:
                        break
                    payload = {
                        "topicCode": "",
                        "batch": str(source.get("batch", "2027")),
                        "campusNature": channel["campus_nature"],
                        "abroad": "",
                        "degree": "",
                        "jobType": [],
                        "researchDirection": [],
                        "workPlace": [],
                        "keywords": "",
                        "pageSize": min(10, max_jobs - len(items)),
                        "pageIndex": 1,
                    }
                    response = await client.post(self._endpoint(source, LIST_PATH), data=payload)
                    if response.status in (403, 429):
                        return CollectionResult([], False, response_urls + [response.url], f"http_{response.status}")
                    body = await response.json()
                    response_urls.append(response.url)
                    rows = body.get("data") if isinstance(body, dict) else None
                    if not isinstance(rows, list):
                        continue
                    for row in rows:
                        if not isinstance(row, dict) or not row.get("id"):
                            continue
                        detail_params = {"id": row["id"], "abroad": "", "degree": ""}
                        detail = await client.get(self._endpoint(source, DETAIL_PATH), params=detail_params)
                        if detail.status in (403, 429):
                            return CollectionResult([], False, response_urls + [detail.url], f"http_{detail.status}")
                        detail_body = await detail.json()
                        response_urls.append(detail.url)
                        outer = detail_body.get("data") if isinstance(detail_body, dict) else None
                        inner_rows = outer.get("positionInfoList") if isinstance(outer, dict) else None
                        if not isinstance(inner_rows, list):
                            continue
                        for inner in inner_rows:
                            if len(items) >= max_jobs or not isinstance(inner, dict) or not inner.get("id"):
                                break
                            raw = {
                                "outer": outer,
                                "inner": inner,
                                "job_nature": channel["job_nature"],
                                "outer_id": str(row["id"]),
                            }
                            apply_url = self._apply_url(source, raw)
                            items.append(
                                ListingItem(
                                    f"{row['id']}:{inner['id']}",
                                    str(outer.get("jobName") or row.get("jobName") or ""),
                                    apply_url,
                                    raw,
                                )
                            )
            finally:
                await client.dispose()
        return CollectionResult(items, False, response_urls)

    def _apply_url(self, source: dict[str, Any], raw: dict[str, Any]) -> str:
        outer = raw.get("outer") or {}
        params = urlencode({"id": raw.get("outer_id") or outer.get("id"), "abroad": "", "degree": ""})
        return f"{self._endpoint(source, DETAIL_PATH)}?{params}"

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        return item.raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        outer = raw.get("outer") or {}
        inner = raw.get("inner") or {}
        title = str(outer.get("jobName") or "").strip()
        description = str(inner.get("jobDuty") or "").strip()
        requirements = str(inner.get("jobRequirements") or "").strip()
        if not title or not (description or requirements):
            return None
        source_job_id = f"{raw.get('outer_id') or outer.get('id')}:{inner.get('id')}"
        canonical = normalize_job(
            {
                "id": source_job_id,
                "title": title,
                "job_type": raw.get("job_nature"),
                "category": str(inner.get("jobType") or outer.get("jobType") or ""),
                "workplace": inner.get("workPlace") or outer.get("workPlace") or "",
                "degree": requirements,
                "description": description,
                "requirements": requirements,
                "apply_url": self._apply_url(source, raw),
                "updated_at": outer.get("updateTime"),
            },
            source,
        )
        if canonical is None:
            return None
        digest = "|".join(str(canonical.get(key) or "") for key in ("company", "title", "city", "job_nature", "source_job_id", "apply_url", "description", "requirements"))
        canonical["content_hash"] = hashlib.sha256(digest.encode("utf-8", "ignore")).hexdigest()
        return canonical


__all__ = ["BydCampusAdapter"]
