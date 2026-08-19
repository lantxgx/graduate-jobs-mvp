"""Conservative parser for Beisen/Zhiye-style campus job payloads.

The adapter is deliberately separated from browser discovery so fixtures can be
validated without contacting a recruitment site. It accepts the common field
aliases seen across Beisen-hosted and self-hosted Zhiye pages, then delegates
canonical field construction to the existing normalizer.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

from crawler.normalize import find_job_dicts, normalize_job


ALIASES = {
    "id": ("jobId", "job_id", "positionId", "position_id", "JobAdId", "id"),
    "title": ("jobName", "job_name", "positionName", "position_name", "JobAdName", "title", "name"),
    "city": ("workCity", "work_city", "LocNames", "city", "workplace", "location"),
    "nature": ("recruitType", "recruit_type", "jobType", "job_type", "Kind", "nature"),
    "category": ("jobCategory", "job_category", "ClassificationOne", "category", "function"),
    "degree": ("education", "educationLevel", "education_level", "Degree", "degree"),
    "description": ("jobDescription", "job_description", "Duty", "description", "responsibility"),
    "requirements": ("jobRequirements", "job_requirements", "Require", "requirements", "qualification"),
    "url": ("detailUrl", "detail_url", "jobUrl", "job_url", "JobAdUrl", "url", "link"),
    "published": ("publishDate", "publish_date", "publishedAt", "published_at", "ChangeDate", "updateTime"),
}


def _value(item: dict[str, Any], keys: tuple[str, ...]) -> Any:
    lowered = {str(key).replace("_", "").lower(): value for key, value in item.items()}
    for key in keys:
        value = lowered.get(key.replace("_", "").lower())
        if value not in (None, "", [], {}):
            if isinstance(value, dict):
                for subkey in ("name", "label", "value", "text"):
                    if value.get(subkey) not in (None, ""):
                        return value[subkey]
            return value
    return None


def _text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, list):
        return " / ".join(str(part) for part in value if part not in (None, "")) or None
    return str(value).strip() or None


def adapt_beisen_job(item: dict[str, Any], source: dict[str, Any]) -> dict[str, Any] | None:
    """Map one Beisen/Zhiye object into the normalizer's accepted aliases."""
    title = _text(_value(item, ALIASES["title"]))
    job_id = _text(_value(item, ALIASES["id"]))
    if not title or not job_id:
        return None
    raw_url = _text(_value(item, ALIASES["url"]))
    detail_fields = (
        _value(item, ALIASES["city"]),
        _value(item, ALIASES["nature"]),
        _value(item, ALIASES["category"]),
        _value(item, ALIASES["degree"]),
        _value(item, ALIASES["description"]),
        _value(item, ALIASES["requirements"]),
    )
    # Beisen pages also expose navigation cards (Campus, city filters, etc.)
    # in the same JSON tree. They are not concrete, transferable positions.
    # Require a detail URL and at least one job-detail field before normalizing.
    if not raw_url or not any(value not in (None, "", [], {}) for value in detail_fields):
        return None
    detail_url = urljoin(source["url"], raw_url) if raw_url else urljoin(source["url"], f"job/{job_id}")
    canonical_input = {
        "id": job_id,
        "title": title,
        "city": _text(_value(item, ALIASES["city"])),
        "job_type": _text(_value(item, ALIASES["nature"])),
        "category": _text(_value(item, ALIASES["category"])),
        "degree": _text(_value(item, ALIASES["degree"])),
        "description": _text(_value(item, ALIASES["description"])),
        "requirements": _text(_value(item, ALIASES["requirements"])),
        "detail_url": detail_url,
        "published_at": _text(_value(item, ALIASES["published"])),
    }
    return normalize_job(canonical_input, source)


def parse_beisen_payload(payload: Any, source: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract and normalize concrete positions from one captured JSON payload."""
    jobs: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in find_job_dicts(payload):
        job = adapt_beisen_job(item, source)
        if not job or job["content_hash"] in seen:
            continue
        seen.add(job["content_hash"])
        jobs.append(job)
    return jobs
