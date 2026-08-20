"""潍柴雷沃旧版北森门户的公开校园岗位页面适配器."""
from __future__ import annotations

import hashlib
from typing import Any
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup, Tag

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_category, normalize_city, normalize_degree, normalize_job, normalize_job_nature


def _text(node: Tag | None) -> str:
    return " ".join(node.get_text(" ", strip=True).split()) if node else ""


class LovolCampusAdapter:
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
        response = await self._get(source["url"], source["url"])
        if response.status_code in (403, 429):
            return CollectionResult([], False, [str(response.url)], f"http_{response.status_code}")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        body = soup.select_one(".gwsec2 .sbody")
        if body is None:
            return CollectionResult([], False, [str(response.url)], "no_concrete_visible_job_cards")
        max_jobs = min(max(int(source.get("max_jobs", 20)), 1), 20)
        children = [x for x in body.find_all(recursive=False) if isinstance(x, Tag)]
        items: list[ListingItem] = []
        for index, heading in enumerate(children):
            if "shd" not in (heading.get("class") or []):
                continue
            detail = children[index + 1] if index + 1 < len(children) else None
            title = _text(heading.select_one(".t"))
            city = _text(heading.select_one(".w3"))
            if not title or detail is None:
                continue
            apply = detail.select_one("a.applybtn[href]")
            apply_url = urljoin(source["url"], apply.get("href")) if apply else ""
            jid = apply.get("href", "") if apply else title
            raw_text = _text(detail)
            items.append(ListingItem(jid, title, apply_url, {
                "id": jid, "title": title, "city": city, "detail_text": raw_text,
                "apply_url": apply_url, "category": _text(heading.select_one(".w2")),
            }))
            if len(items) >= max_jobs:
                break
        if not items:
            return CollectionResult([], False, [str(response.url)], "no_concrete_visible_job_cards")
        return CollectionResult(items, False, [str(response.url)])

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        return item.raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        text = str(raw.get("detail_text") or "")
        duty, req = text, ""
        for marker in ("任职资格：", "任职资格:", "任职要求：", "任职要求:"):
            if marker in text:
                duty, req = text.split(marker, 1)
                break
        title = str(raw.get("title") or "").strip()
        city = str(raw.get("city") or "").strip()
        category_raw = str(raw.get("category") or "").strip()
        nature = normalize_job_nature("校园招聘", title, duty + req)
        if not title or not raw.get("apply_url") or not (duty or req) or not nature:
            return None
        item = {"id": str(raw.get("id") or ""), "company": source["company"], "title": title,
                "city": normalize_city(city), "job_nature": nature,
                "category": normalize_category(category_raw, title, duty),
                "degree": normalize_degree("", req), "description": duty,
                "requirements": req, "apply_url": raw["apply_url"],
                "source_url": source["url"], "source_job_id": str(raw.get("id") or ""),
                "published_at": None}
        digest = "|".join(str(item.get(k) or "") for k in ("company", "title", "city", "job_nature", "source_job_id", "apply_url", "description", "requirements"))
        item["content_hash"] = hashlib.sha256(digest.encode()).hexdigest()
        item["source_id"] = source["id"]
        item["raw"] = raw
        return normalize_job(item, source)


__all__ = ["LovolCampusAdapter"]
