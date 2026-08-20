"""Export the first reviewable company set in the canonical job-record format."""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db import DB_PATH
from crawler.normalize import extract_major_requirements, split_location_records


BLOCKED_REVIEW_SOURCES = ("哔哩哔哩", "完美世界")


def split_text(value: str | None) -> list[str]:
    return [line.strip(" -•·\t") for line in (value or "").replace("\r", "").split("\n") if line.strip()]


def canonical_job(row: sqlite3.Row) -> dict:
    location_hierarchy = split_location_records(row["city"])
    locations = [location["city"] for location in location_hierarchy]
    responsibilities = split_text(row["description"])
    qualifications = split_text(row["requirements"])
    if not responsibilities:
        responsibilities = ["官方页面未单独拆分岗位职责，详见岗位详情。"]
    if not qualifications:
        qualifications = ["官方页面未单独拆分任职要求，详见岗位详情。"]
    return {
        "record_version": "1.0",
        "source_id": row["source_id"],
        "source_job_id": row["source_job_id"] or str(row["id"]),
        "company": row["company"],
        "title": row["title"],
        "work_locations": locations,
        "location_hierarchy": location_hierarchy,
        "location_status": "stated" if locations else "not_stated",
        "job_function": row["category"] or "其他",
        "job_nature": row["job_nature"],
        "degree": row["degree"] or "未注明",
        "major_requirements": extract_major_requirements(row["requirements"]),
        "responsibilities": responsibilities,
        "qualifications": qualifications,
        "graduate_year": row["graduate_year"],
        "published_at": row["published_at"],
        "deadline": None,
        "apply_url": row["apply_url"],
        "source_url": row["source_url"],
        "status": "accepted",
        "evidence": {
            "listing_url": row["source_url"],
            "detail_url": row["apply_url"],
            "captured_at": row["last_seen_at"],
            "raw_hash": row["content_hash"],
        },
    }


def export(limit: int, output: Path) -> dict:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        companies = [r[0] for r in conn.execute(
            "SELECT company FROM jobs WHERE status='active' GROUP BY company ORDER BY COUNT(*) DESC LIMIT ?",
            (limit,),
        ).fetchall()]
        rows = conn.execute(
            "SELECT * FROM jobs WHERE status='active' ORDER BY company, id DESC"
        ).fetchall()
    by_company = {name: [] for name in companies}
    for row in rows:
        if row["company"] in by_company:
            by_company[row["company"]].append(canonical_job(row))
    for name in BLOCKED_REVIEW_SOURCES:
        if len(by_company) >= limit:
            break
        by_company.setdefault(name, [])
    payload = {
        "format": "graduate-radar.standardized-companies",
        "record_version": "1.0",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "companies": [
            {"company": name, "status": "accepted" if jobs else "blocked", "jobs": jobs}
            for name, jobs in by_company.items()
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--output", default="data/standardized/companies-10.json")
    args = parser.parse_args()
    payload = export(args.limit, Path(args.output))
    print(json.dumps({"output": args.output, "companies": len(payload["companies"]), "jobs": sum(len(x["jobs"]) for x in payload["companies"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
