"""Lenovo public campus recruitment adapter."""
from __future__ import annotations

import hashlib
import html
import re
from typing import Any
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_category, normalize_city, normalize_degree, normalize_job_nature


CITY_CODES = {1: chr(0x5317)+chr(0x4eac), 2: chr(0x4e0a)+chr(0x6d77), 3: chr(0x5e7f)+chr(0x5dde), 4: chr(0x91cd)+chr(0x5e86), 5: chr(0x6df1)+chr(0x5733), 6: chr(0x5929)+chr(0x6d25), 7: chr(0x6210)+chr(0x90fd), 8: chr(0x6b66)+chr(0x6c49), 9: chr(0x60e0)+chr(0x5dde), 10: chr(0x53a6)+chr(0x95e8), 12: chr(0x676d)+chr(0x5dde), 20: chr(0x5357)+chr(0x4eac), 22: chr(0x5408)+chr(0x80a5), 23: chr(0x82cf)+chr(0x5dde), 25: chr(0x6d4e)+chr(0x5357), 32: chr(0x65e0)+chr(0x9521)}


def _strip(value: Any) -> str:
    text = html.unescape(str(value or ""))
    return re.sub(r"<[^>]+>", "", text).replace("\xa0", " ").strip()


def normalize_lenovo_job(raw: dict[str, Any], source: dict[str, Any]) -> dict[str, Any] | None:
    job_id = str(raw.get("id") or "").strip()
    title = _strip(raw.get("jobName"))
    duties = _strip(raw.get("jobDuties"))
    requirements = _strip(raw.get("jobRequirement"))
    if not job_id or not title or not (duties or requirements):
        return None
    cities = [CITY_CODES.get(int(x), x) for x in str(raw.get("workPlace") or "").split(",") if str(x).strip()]
    city = normalize_city(" / ".join(cities) or None)
    # Lenovo's projectType=1 endpoint is the graduate full-time channel;
    # the listing label is "应届", which is not itself a contract value.
    nature = chr(0x5168) + chr(0x804c)
    apply_url = urljoin(source["url"], f"/position/detail?id={job_id}")
    canonical = {
        "company": source["company"], "title": title[:160], "city": city,
        "job_nature": nature, "category": normalize_category(raw.get("typeName"), title, duties + " " + requirements),
        "degree": normalize_degree(None, requirements), "graduate_year": None,
        "requirements": requirements or None, "description": duties or None,
        "apply_url": apply_url, "source_url": source["url"], "source_job_id": job_id,
        "published_at": None,
    }
    digest = "|".join(str(canonical.get(k) or "") for k in ("company", "title", "city", "job_nature", "source_job_id", "apply_url"))
    canonical["content_hash"] = hashlib.sha256(digest.encode("utf-8")).hexdigest()
    canonical["source_id"] = source["id"]
    canonical["raw"] = raw
    return canonical


class LenovoAdapter:
    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        import asyncio, json
        def fetch(page: int) -> dict[str, Any]:
            url = f"https://talent.lenovo.com.cn/gateway/jobBase/list?projectType=1&pageNum={page}"
            req = Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": source["url"]})
            with urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        first = await asyncio.to_thread(fetch, 1)
        result = first.get("result") or {}
        total = int(result.get("total") or 0)
        page_size = len(result.get("rows") or []) or 10
        pages = max(1, (total + page_size - 1) // page_size)
        records = list(result.get("rows") or [])
        for page in range(2, pages + 1):
            payload = await asyncio.to_thread(fetch, page)
            records.extend((payload.get("result") or {}).get("rows") or [])
        items = [ListingItem(str(r.get("id")), str(r.get("jobName") or ""), urljoin(source["url"], f"/position/detail?id={r.get('id')}"), r) for r in records if isinstance(r, dict) and r.get("id")]
        return CollectionResult(items, len(items) == total, ["https://talent.lenovo.com.cn/gateway/jobBase/list?projectType=1&pageNum=1"])

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        return item.raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        return normalize_lenovo_job(raw, source)


__all__ = ["LenovoAdapter", "normalize_lenovo_job"]
