"""Bounded parser for the legacy public GAC Toyota Beisen portal."""

from __future__ import annotations

import hashlib
import re
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_degree, normalize_job_nature, normalize_location_name


def _text(node: Any) -> str:
    return re.sub(r"\s+", " ", node.get_text(" ", strip=True) if node else "").strip()


def _section(soup: BeautifulSoup, label: str) -> str:
    for title in soup.select(".xiangqingtext .title"):
        if _text(title) == label:
            paragraph = title.find_next("p")
            return _text(paragraph)
    return ""


class GacToyotaCampusAdapter:
    async def _get_html(self, url: str) -> str:
        async with async_playwright() as pw:
            request = await pw.request.new_context(timeout=30000)
            try:
                response = await request.get(url, headers={"User-Agent": "Mozilla/5.0"})
                if response.status in (403, 429):
                    raise RuntimeError(f"http_{response.status}")
                if not response.ok:
                    raise RuntimeError(f"http_{response.status}")
                return await response.text()
            finally:
                await request.dispose()

    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        try:
            html = await self._get_html(source["url"])
        except RuntimeError as exc:
            return CollectionResult([], False, [source["url"]], str(exc))
        soup = BeautifulSoup(html, "html.parser")
        items: list[ListingItem] = []
        for row in soup.select("table.jobsTable tr"):
            link = row.select_one('a[href*="/zpdetail/"]')
            if not link:
                continue
            href = urljoin(source["url"], str(link.get("href") or ""))
            match = re.search(r"/zpdetail/([^/?#]+)", href)
            if not match:
                continue
            cells = row.find_all("td")
            items.append(ListingItem(
                match.group(1),
                _text(link)[:160],
                href,
                {
                    "location": _text(cells[2]) if len(cells) > 2 else "",
                    "published_at": _text(cells[3]) if len(cells) > 3 else "",
                },
            ))
            if len(items) >= min(max(int(source.get("max_jobs", 20)), 1), 20):
                break
        if not items:
            return CollectionResult([], False, [source["url"]], "no_concrete_public_campus_jobs")
        # The old portal has no reliable total/pagination signal in this view.
        return CollectionResult(items, False, [source["url"]])

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        html = await self._get_html(item.detail_url)
        soup = BeautifulSoup(html, "html.parser")
        title = _text(soup.select_one(".boxSupertitle")) or item.title
        values: dict[str, str] = {}
        for label in soup.select(".xiangqinglist .ntitle"):
            value = label.find_next_sibling(class_="nvalue") or label.find_next_sibling(class_="nvcity")
            values[_text(label).rstrip("：:")] = _text(value)
        return {
            "source_job_id": item.source_job_id,
            "title": title,
            "recruitment_category": values.get("招聘类别", ""),
            "job_nature_raw": values.get("工作性质", ""),
            "location": values.get("工作地点", "") or item.raw.get("location", ""),
            "published_at": values.get("发布时间", "") or item.raw.get("published_at", ""),
            "description": _section(soup, "工作职责："),
            "requirements": _section(soup, "任职资格："),
            "apply_url": item.detail_url,
            "raw_html_evidence": {
                "detail_url": item.detail_url,
                "recruitment_category": values.get("招聘类别", ""),
                "job_nature": values.get("工作性质", ""),
                "location": values.get("工作地点", ""),
                "published_at": values.get("发布时间", ""),
            },
        }

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        title = str(raw.get("title") or "").strip()
        description = str(raw.get("description") or "").strip()
        requirements = str(raw.get("requirements") or "").strip()
        job_id = str(raw.get("source_job_id") or "").strip()
        location = normalize_location_name(raw.get("location"))
        nature = normalize_job_nature(raw.get("job_nature_raw") or raw.get("recruitment_category"), title, description)
        if not all((title, description, requirements, job_id, location, nature)):
            return None
        canonical = {
            "company": source["company"],
            "title": title[:160],
            "city": location,
            "job_nature": nature,
            "category": "硬件研发",
            "degree": normalize_degree(None, requirements),
            "graduate_year": None,
            "requirements": requirements,
            "description": description,
            "apply_url": str(raw.get("apply_url") or ""),
            "source_url": source["url"],
            "source_job_id": job_id,
            "published_at": raw.get("published_at") or None,
            "source_id": source["id"],
            "raw": raw,
        }
        if not canonical["apply_url"]:
            return None
        digest = "|".join(str(canonical.get(key) or "") for key in (
            "company", "title", "city", "job_nature", "category", "degree",
            "source_job_id", "apply_url", "description", "requirements",
        ))
        canonical["content_hash"] = hashlib.sha256(digest.encode("utf-8")).hexdigest()
        return canonical


__all__ = ["GacToyotaCampusAdapter"]
