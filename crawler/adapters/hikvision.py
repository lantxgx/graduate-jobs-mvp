"""Public Hikvision campus position API adapter."""
from __future__ import annotations
import hashlib
from typing import Any
from playwright.async_api import async_playwright
from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_category, normalize_city, normalize_degree, normalize_job_nature

ENDPOINT = "/api/search/crsPositionSearch/getPositionByQuery"

def normalize_hikvision_job(raw: dict[str, Any], source: dict[str, Any]) -> dict[str, Any] | None:
    jid = str(raw.get("id") or "").strip(); title = str(raw.get("postAdName") or "").strip()
    if not jid or not title: return None
    desc = str(raw.get("postContent") or "").strip(); req = str(raw.get("postRequire") or "").strip()
    nature = normalize_job_nature(str(raw.get("jobNature") or ""), title, desc + req)
    if not nature or not (desc or req): return None
    places = raw.get("workPlaceList") or raw.get("workPlace") or ""
    city = normalize_city(" / ".join(map(str, places)) if isinstance(places, list) else str(places))
    apply_url = str(raw.get("attr2") or source["url"]).strip()
    item = {"company": source["company"], "title": title[:160], "city": city, "job_nature": nature,
            "category": normalize_category(str(raw.get("postAdSn") or ""), title, desc),
            "degree": normalize_degree(str(raw.get("requiireEdu") or ""), req), "graduate_year": None,
            "requirements": req or None, "description": desc or None, "apply_url": apply_url,
            "source_url": source["url"], "source_job_id": jid, "published_at": str(raw.get("updateTime") or "") or None}
    digest = "|".join(str(item.get(k) or "") for k in ("company","title","city","job_nature","source_job_id","apply_url"))
    item["content_hash"] = hashlib.sha256(digest.encode()).hexdigest(); item["source_id"] = source["id"]; item["raw"] = raw
    return item

class HikvisionAdapter:
    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        from urllib.parse import urlsplit, urlunsplit
        p = urlsplit(source["url"]); endpoint = urlunsplit((p.scheme,p.netloc,ENDPOINT,"",""))
        payload = {"batchId":"", "postAdSnList":"", "interviewMethodList":"", "keyWord":"", "jobNature":"应届生", "pageNum":1, "pageSize":min(int(source.get("max_jobs",20)),20)}
        async with async_playwright() as pw:
            req = await pw.request.new_context()
            try:
                r = await req.post(endpoint, form=payload, timeout=30000)
                if r.status in (403,429): return CollectionResult([],False,[endpoint],f"http_{r.status}")
                body = await r.json()
            finally: await req.dispose()
        rows = ((body.get("data") or {}).get("list") if isinstance(body,dict) else None) or []
        total = int(((body.get("data") or {}).get("total") or len(rows))) if isinstance(body,dict) else 0
        items = [ListingItem(str(x.get("id")),str(x.get("postAdName") or ""),str(x.get("attr2") or source["url"]),x) for x in rows if isinstance(x,dict) and x.get("id")]
        return CollectionResult(items,total <= len(items),[endpoint])
    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]: return item.raw
    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None: return normalize_hikvision_job(raw, source)
