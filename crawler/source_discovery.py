from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


ATS_BY_MARKER = (
    ("feishu", ("jobs.feishu.cn", "jobs.f.mioffice.cn")),
    ("beisen", ("zhiye.com",)),
    ("moka", ("mokahr.com",)),
    ("greenhouse", ("greenhouse.io",)),
    ("lever", ("lever.co",)),
    ("ashby", ("ashbyhq.com",)),
    ("workday", ("myworkdayjobs.com",)),
)


@dataclass(frozen=True)
class SourceCandidate:
    company_name: str
    url: str
    evidence_url: str | None
    ats_type: str
    official_status: str
    discovery_source: str


def classify_ats(url: str, page_title: str = "", html: str = "") -> str:
    haystack = " ".join((url, page_title, html)).lower()
    for ats_type, markers in ATS_BY_MARKER:
        if any(marker in haystack for marker in markers):
            return ats_type
    return "custom"


def _host(url: str) -> str:
    return (urlparse(url).hostname or "").lower().removeprefix("www.")


def verify_official_ownership(company: dict, candidate: dict) -> bool:
    """Conservative ownership check; it never treats a search result alone as official."""
    official_host = _host(str(company.get("official_website") or ""))
    evidence_url = str(candidate.get("evidence_url") or "")
    candidate_host = _host(str(candidate.get("url") or ""))
    evidence_host = _host(evidence_url)
    if not official_host or not candidate_host or not evidence_host:
        return False
    return official_host == evidence_host or official_host == candidate_host


def import_company_candidates(path: Path) -> list[dict]:
    required = {"canonical_name", "brand_name", "official_website"}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError("company_candidate_csv_missing_required_columns")
        rows = []
        for row in reader:
            name = (row.get("canonical_name") or "").strip()
            website = (row.get("official_website") or "").strip()
            if not name or not website:
                continue
            rows.append({key: (value or "").strip() for key, value in row.items()})
        return rows


def make_candidate(company: dict, url: str, evidence_url: str | None, discovery_source: str) -> SourceCandidate:
    official = verify_official_ownership(
        company,
        {"url": url, "evidence_url": evidence_url},
    )
    return SourceCandidate(
        company_name=str(company.get("canonical_name") or company.get("brand_name") or ""),
        url=url,
        evidence_url=evidence_url,
        ats_type=classify_ats(url),
        official_status="confirmed" if official else "candidate",
        discovery_source=discovery_source,
    )
