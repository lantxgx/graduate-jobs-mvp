"""Public Kuaishou campus recruitment API adapter."""
from __future__ import annotations

import hashlib
import json
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from playwright.async_api import async_playwright

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_job


LIST_PATH = "/recruit/campus/e/api/v1/open/positions/simple"
DETAIL_PATH = "/recruit/campus/e/api/v1/open/positions/find"
DEFAULT_PROJECT_CODE = "20271779425607"


class KuaishouCampusAdapter:
    def _endpoint(self, source: dict[str, Any], path: str) -> str:
        parsed = urlsplit(source["url"])
        return urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))

    def _detail_url(self, source: dict[str, Any], row: dict[str, Any]) -> str:
        code = str(row.get("code") or "")
        project = str(row.get("recruitSubProjectCode") or DEFAULT_PROJECT_CODE)
        return (
            f"{source['url'].split('#', 1)[0]}#/campus/job-info/{row.get('id')}"
            f"?code={code}&recruitSubProjectCodes={project}"
        )

    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        limit = min(max(int(source.get("max_jobs", 20)), 1), 20)
        projects = source.get("recruit_sub_project_codes") or [DEFAULT_PROJECT_CODE]
        payload = {
            "recruitSubProjectCodes": [str(value) for value in projects],
            "pageSize": limit,
            "pageNum": 1,
        }
        endpoint = self._endpoint(source, LIST_PATH)
        detail_endpoint = self._endpoint(source, DETAIL_PATH)
        headers = {"User-Agent": "Mozilla/5.0", "Referer": source["url"]}
        rows: list[dict[str, Any]] = []
        response_urls = [endpoint]
        async with async_playwright() as pw:
            request = await pw.request.new_context(extra_http_headers=headers, timeout=30000)
            try:
                response = await request.post(
                    endpoint,
                    data=json.dumps(payload),
                    headers={"Content-Type": "application/json"},
                )
                if response.status in (403, 429):
                    return CollectionResult([], False, response_urls, f"http_{response.status}")
                body = json.loads((await response.body()).decode("utf-8"))
                result = body.get("result") if isinstance(body, dict) else None
                listed = result.get("list") if isinstance(result, dict) else None
                if not isinstance(listed, list):
                    return CollectionResult([], False, response_urls, "no_concrete_visible_job_cards")
                for row in listed[:limit]:
                    if not isinstance(row, dict) or not row.get("id") or not row.get("name"):
                        continue
                    detail = await request.get(
                        detail_endpoint,
                        params={"id": str(row["id"]), "positionStatus": "Release"},
                    )
                    response_urls.append(detail.url)
                    if detail.status in (403, 429):
                        return CollectionResult([], False, response_urls, f"http_{detail.status}")
                    detail_body = json.loads((await detail.body()).decode("utf-8"))
                    detail_row = detail_body.get("result") if isinstance(detail_body, dict) else None
                    if isinstance(detail_row, dict):
                        rows.append(detail_row)
            finally:
                await request.dispose()
        items = [
            ListingItem(str(row["id"]), str(row.get("name") or ""), self._detail_url(source, row), row)
            for row in rows
        ]
        return CollectionResult(items, False, response_urls)

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        return item.raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        title = str(raw.get("name") or "").strip()
        description = str(raw.get("description") or "").strip()
        requirements = str(raw.get("positionDemand") or "").strip()
        locations = raw.get("workLocationDicts") or []
        workplace = " / ".join(
            str(row.get("name") or "").strip()
            for row in locations
            if isinstance(row, dict) and str(row.get("name") or "").strip()
        )
        if not title or not (description and requirements) or not workplace:
            return None
        project = str(raw.get("recruitSubProjectCode") or DEFAULT_PROJECT_CODE)
        job_type = "实习" if str(raw.get("positionNatureCode")) == "intern" else "全职"
        canonical = normalize_job(
            {
                "id": str(raw.get("id")),
                "title": title,
                "job_type": job_type,
                "category": "",
                "workplace": workplace,
                "degree": requirements,
                "description": description,
                "requirements": requirements,
                "apply_url": self._detail_url(source, raw),
                "updated_at": raw.get("updateTime") or raw.get("releaseTime"),
                "published_at": raw.get("releaseTime"),
            },
            source,
        )
        if canonical is None:
            return None
        digest = "|".join(
            str(canonical.get(key) or "")
            for key in ("company", "title", "city", "job_nature", "source_job_id", "apply_url", "description", "requirements")
        )
        canonical["content_hash"] = hashlib.sha256(digest.encode("utf-8", "ignore")).hexdigest()
        return canonical


__all__ = ["KuaishouCampusAdapter"]
