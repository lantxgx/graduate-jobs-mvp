from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class ListingItem:
    source_job_id: str
    title: str
    detail_url: str
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class CollectionResult:
    listing_items: list[ListingItem]
    snapshot_complete: bool
    response_urls: list[str] = field(default_factory=list)
    stop_reason: str | None = None


class JobSourceAdapter(Protocol):
    async def fetch_listing(self, source: dict[str, Any]) -> CollectionResult: ...
    async def fetch_detail(self, source: dict[str, Any], item: ListingItem) -> dict[str, Any]: ...
    def normalize(self, source: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None: ...


class AdapterRegistry:
    def __init__(self):
        self._adapters: dict[str, JobSourceAdapter] = {}

    def register(self, name: str, adapter: JobSourceAdapter) -> None:
        self._adapters[name] = adapter

    def get(self, name: str) -> JobSourceAdapter:
        try:
            return self._adapters[name]
        except KeyError as exc:
            raise KeyError(f"unknown_source_adapter:{name}") from exc

    def names(self) -> list[str]:
        return sorted(self._adapters)
