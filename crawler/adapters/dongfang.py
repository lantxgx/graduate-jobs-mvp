"""Adapter for the official Dongfang Electric campus announcement page."""

from __future__ import annotations

import re
from typing import Any

import httpx
from bs4 import BeautifulSoup

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_job


class DongfangCampusAdapter:
    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        headers = {"User-Agent": "Mozilla/5.0"}
        async with httpx.AsyncClient(timeout=30, headers=headers, follow_redirects=True) as client:
            response = await client.get(source["url"])
        if response.status_code in (403, 429):
            return CollectionResult([], False, [str(response.url)], f"http_{response.status_code}")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        text = " ".join(soup.get_text(" ", strip=True).split())
        if "校园招聘" not in text or "工作地点" not in text or "任职条件" not in text:
            return CollectionResult([], False, [str(response.url)], "public_job_detail_missing")
        title = soup.title.get_text(" ", strip=True).split("-")[0].strip() if soup.title else ""
        title = title.replace("-中国东方电气集团有限公司", "").strip()
        m = re.search(r"校园招聘([^ ]*?)的公告", title)
        if m:
            title = m.group(1) + "校园招聘"
        city_m = re.search(r"工作地点\s+([^。；]+)", text)
        req_m = re.search(r"任职条件\s+(.*?)(?=四、招聘程序)", text)
        desc_m = re.search(r"岗位职责：\s*(.*?)(?=2\.任职条件：)", text)
        raw = {
            "id": "20719",
            "title": title or "校园招聘宣传干事",
            "city": city_m.group(1).strip() if city_m else "",
            "job_type": "校园招聘",
            "description": desc_m.group(1).strip() if desc_m else text,
            "requirements": req_m.group(1).strip() if req_m else "",
            "detail_url": source["url"],
        }
        return CollectionResult([ListingItem("20719", raw["title"], source["url"], raw)], False, [str(response.url)])

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        return item.raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        return normalize_job(raw, source)


__all__ = ["DongfangCampusAdapter"]
