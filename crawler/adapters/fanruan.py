"""Fanruan official campus recruitment adapter.

The public campus page renders its list with a same-origin POST after the
initial GET.  The GET sets a public cookie used by the POST, so the adapter
keeps one normal HTTP session for the bounded list and detail requests.
"""

from __future__ import annotations

import asyncio
import hashlib
import re
from typing import Any
from urllib.parse import urljoin
from urllib.parse import urlencode

import httpx
from bs4 import BeautifulSoup

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import (
    COUNTRY_ALIASES,
    JOB_NATURE_FULL_TIME,
    normalize_category,
    normalize_city,
    normalize_degree,
    normalize_job_nature,
    split_location_records,
)


PAGE_SIZE = 10


def _text(node: Any) -> str:
    if node is None:
        return ""
    return re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip()


def _section(soup: BeautifulSoup, heading: str) -> str:
    for main in soup.select(".job-main"):
        title = _text(main.select_one(".job-sub-title"))
        if heading in title:
            return _text(main.select_one(".job-sub-desc"))
    return ""


def _fanruan_locations(value: str) -> str:
    # These are scope labels shown alongside actual cities, not cities.  Keep
    # the evidenced city entries and let the quality gate reject a record if
    # only a scope label remains.
    scopes = {
        "全国", "国内", "港澳台地区", "海外地区", "海外",
        "台湾地区", "香港地区", "澳门地区",
    }
    values = []
    for item in re.split(r"[/|,，、;；]+", value):
        item = item.strip()
        if item and item not in scopes and item.lower() not in COUNTRY_ALIASES and item not in values:
            values.append(item)
    return " / ".join(values)


def parse_fanruan_detail(page_html: str) -> dict[str, str]:
    soup = BeautifulSoup(page_html, "html.parser")
    base = {"detail_title": _text(soup.select_one(".job-title"))}
    base["detail_description"] = _section(soup, "职位介绍")
    base["detail_duty"] = _section(soup, "岗位职责")
    base["detail_requirement"] = _section(soup, "岗位要求")
    location = ""
    for row in soup.select(".job-desc-extra p"):
        label = _text(row.select_one("span:first-child"))
        if "工作地点" in label:
            spans = row.select(".job-info")
            location = _text(spans[0] if spans else row)
            break
    if location:
        base["detail_location"] = location
    submit = soup.select_one("a.detail-toudi-btn[href]")
    if submit and submit.get("href"):
        base["detail_submit"] = submit["href"].strip()
    return base


def normalize_fanruan_job(raw: dict[str, Any], source: dict[str, Any]) -> dict[str, Any] | None:
    job_id = str(raw.get("id") or "").strip()
    title = str(raw.get("detail_title") or raw.get("job_name") or "").strip()
    duty = str(raw.get("detail_duty") or raw.get("duty") or "").strip()
    description = str(raw.get("detail_description") or raw.get("description") or duty).strip()
    requirements = str(raw.get("detail_requirement") or raw.get("requirement") or "").strip()
    if not job_id or not title or not description or not requirements:
        return None

    combined = f"{title} {description} {requirements}"
    nature = normalize_job_nature(str(raw.get("mode") or ""), title, combined)
    # Fanruan separates 校招 and 实习生招聘 in the official navigation; the
    # campus source's explicit mode is therefore the full-time graduate path.
    if nature is None and str(raw.get("mode") or "").strip() == "校招":
        nature = JOB_NATURE_FULL_TIME
    if nature is None:
        return None
    city_text = _fanruan_locations(str(raw.get("detail_location") or raw.get("base") or "").strip())
    city_value = normalize_city(city_text)
    city_records = split_location_records(city_value)
    city_value = " / ".join(record["city"] for record in city_records if record.get("city")) or None
    apply_url = str(raw.get("detail_submit") or raw.get("submit") or "").strip()
    detail_url = urljoin(source["url"], f"/campus/detail?id={job_id}")
    if not apply_url:
        apply_url = detail_url
    else:
        apply_url = urljoin(source["url"], apply_url)
    year_match = re.search(r"(20\d{2})\s*届", combined)
    canonical = {
        "company": source["company"],
        "title": title[:160],
        "city": city_value,
        "job_nature": nature,
        "category": normalize_category(str(raw.get("job_type") or ""), title, combined),
        "degree": normalize_degree(None, requirements),
        "graduate_year": year_match.group(1) if year_match else None,
        "requirements": requirements,
        "description": description,
        "apply_url": apply_url,
        "source_url": source["url"],
        "source_job_id": job_id,
        "published_at": None,
    }
    digest = "|".join(str(canonical.get(key) or "") for key in (
        "company", "title", "city", "job_nature", "source_job_id", "apply_url",
    ))
    canonical["content_hash"] = hashlib.sha256(digest.encode("utf-8")).hexdigest()
    canonical["source_id"] = source["id"]
    canonical["raw"] = raw
    return canonical


class FanruanAdapter:
    def __init__(self) -> None:
        self._client = httpx.Client(timeout=30.0, follow_redirects=True, headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html,application/xhtml+xml,application/json,*/*",
        })

    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        url = source["url"]
        response_urls = [url]
        try:
            await asyncio.to_thread(self._client.get, url)
        except Exception as exc:
            return CollectionResult([], False, response_urls, f"public_job_page_request_failed:{type(exc).__name__}")
        categories = source.get("job_categories") or ["5", "1"]
        max_pages = min(max(int(source.get("max_pages", 10)), 1), 20)
        records: dict[str, dict[str, Any]] = {}
        reported_total: int | None = None
        page_total: int | None = None
        for page in range(1, max_pages + 1):
            form: list[tuple[str, str]] = [("job_cate[]", str(value)) for value in categories]
            form.extend([("filter", "1"), ("page", str(page)), ("w", ""), ("cv", "")])
            try:
                response = await asyncio.to_thread(
                    self._client.post,
                    url,
                    content=urlencode(form).encode("utf-8"),
                    headers={
                        "Referer": url,
                        "X-Requested-With": "XMLHttpRequest",
                        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    },
                )
            except Exception as exc:
                return CollectionResult([], False, response_urls, f"public_job_list_request_failed:{type(exc).__name__}")
            response_urls.append(str(response.url))
            if response.status_code in {403, 429}:
                return CollectionResult([], False, response_urls, f"http_{response.status_code}")
            if response.status_code != 200:
                return CollectionResult([], False, response_urls, f"http_{response.status_code}")
            try:
                payload = response.json()
            except ValueError:
                return CollectionResult([], False, response_urls, "public_job_list_invalid_json")
            rows = payload.get("list") if isinstance(payload, dict) else None
            if not isinstance(rows, list):
                return CollectionResult([], False, response_urls, "public_job_list_missing_rows")
            if reported_total is None:
                reported_total = int(payload.get("dataTotal") or 0)
                page_total = int(payload.get("pageTotal") or 0)
            if int(payload.get("dataTotal") or 0) != reported_total:
                return CollectionResult([], False, response_urls, "fanruan_source_count_changed")
            before = len(records)
            for row in rows:
                if not isinstance(row, dict):
                    continue
                job_id = str(row.get("id") or "").strip()
                if job_id:
                    records.setdefault(job_id, dict(row))
            if reported_total == len(records) and page >= (page_total or 1):
                break
            if not rows or len(records) == before:
                return CollectionResult([], False, response_urls, "fanruan_pagination_ended_before_source_count")
        else:
            return CollectionResult([], False, response_urls, "fanruan_page_limit_before_source_count")
        if reported_total is None or len(records) != reported_total:
            return CollectionResult([], False, response_urls, "fanruan_listing_count_unreconciled")
        items = []
        for job_id, raw in records.items():
            detail_url = urljoin(url, f"/campus/detail?id={job_id}")
            items.append(ListingItem(job_id, str(raw.get("job_name") or ""), detail_url, raw))
        return CollectionResult(items, True, response_urls)

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        raw = dict(item.raw)
        response = await asyncio.to_thread(
            self._client.get,
            item.detail_url,
            headers={"Referer": source["url"]},
        )
        if response.status_code in {403, 429}:
            raise RuntimeError(f"http_{response.status_code}")
        if response.status_code != 200:
            raise RuntimeError(f"http_{response.status_code}")
        raw.update(parse_fanruan_detail(response.text))
        return raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        return normalize_fanruan_job(raw, source)


__all__ = ["FanruanAdapter", "normalize_fanruan_job", "parse_fanruan_detail"]
