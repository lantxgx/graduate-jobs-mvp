"""Public Wind campus recruitment page adapter."""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any
from urllib.parse import urljoin

from playwright.async_api import async_playwright

from crawler.adapters.base import CollectionResult, ListingItem
from crawler.normalize import normalize_job


ASSET_PATH = "./js/channelPositions.js?v=20251210"


class WindCampusAdapter:
    def _detail_url(self, source: dict[str, Any], row: dict[str, Any]) -> str:
        return (
            f"{source['url']}?positionType=9002"
            f"&channelPositionId={row.get('ChannelPositionID')}"
        )

    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult:
        limit = min(max(int(source.get("max_jobs", 20)), 1), 20)
        asset_url = urljoin(source["url"], ASSET_PATH)
        async with async_playwright() as pw:
            request = await pw.request.new_context(
                extra_http_headers={"User-Agent": "Mozilla/5.0", "Referer": source["url"]},
                timeout=30000,
            )
            try:
                response = await request.get(asset_url)
                if response.status in (403, 429):
                    return CollectionResult([], False, [asset_url], f"http_{response.status}")
                text = (await response.body()).decode("utf-8")
            finally:
                await request.dispose()
        match = re.search(r"var channelPositions = (\[.*?\]); if \(typeof", text, re.S)
        if not match:
            return CollectionResult([], False, [asset_url], "no_public_position_payload")
        try:
            rows = json.loads(match.group(1))
        except json.JSONDecodeError:
            return CollectionResult([], False, [asset_url], "invalid_public_position_payload")
        if not isinstance(rows, list):
            return CollectionResult([], False, [asset_url], "no_concrete_visible_job_cards")
        selected = [
            row for row in rows
            if isinstance(row, dict)
            and row.get("ChannelPositionID")
            and row.get("PositionType") == 9002
            and row.get("InUse") is not False
            and row.get("ExpireFlag") is not True
            and row.get("ChannelPositionName")
        ][:limit]
        items = [
            ListingItem(
                str(row["ChannelPositionID"]),
                str(row.get("ChannelPositionName") or ""),
                self._detail_url(source, row),
                row,
            )
            for row in selected
        ]
        if not items:
            return CollectionResult([], False, [asset_url], "no_concrete_visible_job_cards")
        return CollectionResult(items, False, [asset_url])

    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]:
        return item.raw

    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
        title = str(raw.get("ChannelPositionName") or raw.get("PositionName") or "").strip()
        description = str(raw.get("ChannelPositionDesc") or "").strip()
        requirements = str(raw.get("ChannelPositionRequirement") or "").strip()
        workplace = " / ".join(
            str(row.get("Name") or "").strip()
            for row in (raw.get("WorkPlace") or [])
            if isinstance(row, dict) and str(row.get("Name") or "").strip()
        )
        if not title or not description or not requirements or not workplace:
            return None
        job_type = "实习" if "实习" in title else "全职"
        canonical = normalize_job(
            {
                "id": str(raw.get("ChannelPositionID")),
                "title": title,
                "job_type": job_type,
                "category": raw.get("PositionClassName") or "",
                "workplace": workplace,
                "degree": raw.get("Degree") or requirements,
                "description": description,
                "requirements": requirements,
                "apply_url": self._detail_url(source, raw),
                "updated_at": raw.get("PublishDate"),
                "published_at": raw.get("PublishDate"),
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


__all__ = ["WindCampusAdapter"]
