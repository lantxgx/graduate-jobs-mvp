"""Baiwang official static campus recruitment page adapter."""
from __future__ import annotations

import hashlib
import re
from html import unescape
from typing import Any

import httpx
from bs4 import BeautifulSoup

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_category, normalize_city, normalize_degree, normalize_job, normalize_job_nature


def _clean_html(value: str) -> str:
    return " ".join(BeautifulSoup(unescape(value or ""), "html.parser").get_text(" ", strip=True).split())


class BaiwangCampusAdapter:
    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        async with httpx.AsyncClient(verify=False, trust_env=False, timeout=30,
                                     headers={"User-Agent": "Mozilla/5.0"}) as client:
            response = await client.get(source["url"])
        if response.status_code in (403, 429):
            return CollectionResult([], False, [str(response.url)], f"http_{response.status_code}")
        response.raise_for_status()
        soup = BeautifulSoup(response.content.decode("utf-8", errors="replace"), "html.parser")
        cards = soup.select(".p_loopitem[data-title]")[:min(max(int(source.get("max_jobs", 20)), 1), 20)]
        items: list[ListingItem] = []
        for card in cards:
            title = str(card.get("data-title") or "").strip()
            if not title:
                continue
            raw = {
                "id": hashlib.sha1(title.encode()).hexdigest()[:20],
                "title": title,
                "category": str(card.get("data-sort1") or "").strip(),
                "degree": str(card.get("data-sort3") or "").strip(),
                "description": _clean_html(str(card.get("data-gw") or "")),
                "requirements": _clean_html(str(card.get("data-zg") or "")),
                "email": str(card.get("data-email") or "").strip(),
                "source_url": source["url"],
            }
            info = card.select(".info > div")
            if len(info) >= 2:
                raw["city"] = " ".join(info[1].get_text(" ", strip=True).split())
            else:
                raw["city"] = ""
            items.append(ListingItem(raw["id"], title, source["url"], raw))
        if not items:
            return CollectionResult([], False, [str(response.url)], "no_concrete_visible_job_cards")
        return CollectionResult(items, len(cards) == len(items) and len(cards) < 20, [str(response.url)])

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        return item.raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        title = str(raw.get("title") or "").strip()
        desc = str(raw.get("description") or "").strip()
        req = str(raw.get("requirements") or "").strip()
        if not title or not (desc or req):
            return None
        nature = normalize_job_nature("校园招聘", title, desc + req)
        if not nature:
            return None
        item = {"id": raw.get("id"), "company": source["company"], "title": title,
                "city": normalize_city(raw.get("city")), "job_nature": nature,
                "category": normalize_category(raw.get("category"), title, desc),
                "degree": normalize_degree(raw.get("degree"), req),
                "description": desc, "requirements": req,
                "apply_url": source["url"], "source_url": source["url"],
                "source_job_id": raw.get("id"), "published_at": None}
        digest = "|".join(str(item.get(k) or "") for k in ("company", "title", "city", "job_nature", "source_job_id", "apply_url", "description", "requirements"))
        item["content_hash"] = hashlib.sha256(digest.encode()).hexdigest()
        item["source_id"] = source["id"]
        item["raw"] = raw
        return normalize_job(item, source)


__all__ = ["BaiwangCampusAdapter"]
