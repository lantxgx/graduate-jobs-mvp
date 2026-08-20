"""Fuyao careers (Tupu360 self-hosted) campus adapter."""
from __future__ import annotations

import hashlib
from typing import Any

import httpx
from bs4 import BeautifulSoup

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_category, normalize_city, normalize_degree, normalize_job, normalize_job_nature


class FuyaoCampusAdapter:
    async def _get(self, url: str, referer: str) -> httpx.Response:
        last: Exception | None = None
        for _ in range(3):
            try:
                async with httpx.AsyncClient(verify=False, trust_env=False, timeout=30,
                                             headers={"User-Agent": "Mozilla/5.0", "Referer": referer}) as client:
                    return await client.get(url)
            except httpx.HTTPError as exc:
                last = exc
        assert last is not None
        raise last

    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        max_jobs = min(max(int(source.get("max_jobs", 20)), 1), 20)
        base = source["base_url"].rstrip("/")
        url = base + "/position/index?recruitmentType=CAMPUSRECRUITMENT"
        response = await self._get(url, source["url"])
        if response.status_code in (403, 429):
            return CollectionResult([], False, [url], f"http_{response.status_code}")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        items: list[ListingItem] = []
        for node in soup.select('.position-item[data-action="positionItem"]')[:max_jobs]:
            pid = (node.get("pid") or "").strip()
            title_node = node.select_one(".position-name .txt")
            title = " ".join(title_node.get_text(" ", strip=True).split()) if title_node else ""
            if not pid or not title:
                continue
            detail = f"{base}/position/detail?positionId={pid}&recruitmentType=CAMPUSRECRUITMENT"
            city_node = node.select_one(".e-city .txt")
            raw = {"id": pid, "title": title, "city": city_node.get_text(" ", strip=True) if city_node else ""}
            items.append(ListingItem(pid, title, detail, raw))
        if not items:
            return CollectionResult([], False, [url], "no_concrete_visible_job_cards")
        count = int((soup.select_one("#position-list") or {}).get("positioncount", len(items)))
        return CollectionResult(items, count <= len(items), [url])

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        response = await self._get(item.detail_url, source["url"])
        if response.status_code in (403, 429):
            return {"_error": f"http_{response.status_code}", "listing": item.raw}
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        box = soup.select_one(".position-details")
        if not box:
            return {"_error": "detail_unavailable", "listing": item.raw}
        paragraphs = [" ".join(p.get_text(" ", strip=True).split()) for p in box.select(".position-description p")]
        paragraphs = [p for p in paragraphs if p]
        text = "\n".join(paragraphs)
        duty, req = text, ""
        if "任职要求" in text:
            duty, req = text.split("任职要求", 1)
        elif "岗位要求" in text:
            duty, req = text.split("岗位要求", 1)
        return {"id": item.source_job_id, "listing": item.raw, "title": item.title, "city": item.raw.get("city", ""),
                "description": duty.replace("岗位职责", "", 1).strip(), "requirements": req.strip(),
                "detail_url": item.detail_url}

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        if raw.get("_error"):
            return None
        listing = raw.get("listing") or {}
        title = str(raw.get("title") or listing.get("title") or "").strip()
        desc = str(raw.get("description") or "").strip()
        req = str(raw.get("requirements") or "").strip()
        nature = normalize_job_nature("校园招聘", title, desc + req)
        if not title or not (desc or req) or not nature:
            return None
        item = {"id": str(listing.get("id") or ""), "company": source["company"], "title": title,
                "city": normalize_city(raw.get("city") or listing.get("city")),
                "job_nature": nature, "category": normalize_category("", title, desc),
                "degree": normalize_degree("", req), "description": desc,
                "requirements": req, "apply_url": raw.get("detail_url"),
                "source_url": source["url"], "source_job_id": str(listing.get("id") or ""),
                "published_at": None}
        digest = "|".join(str(item.get(k) or "") for k in ("company", "title", "city", "job_nature", "source_job_id", "apply_url", "description", "requirements"))
        item["content_hash"] = hashlib.sha256(digest.encode()).hexdigest()
        item["source_id"] = source["id"]
        item["raw"] = raw
        return normalize_job(item, source)


__all__ = ["FuyaoCampusAdapter"]
