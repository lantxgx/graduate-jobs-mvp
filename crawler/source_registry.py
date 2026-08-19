"""Register configured crawler sources in the database without enabling them.

The JSON source file is the execution configuration, while ``career_sources``
is the auditable product registry.  Keeping them synchronized makes the
management page useful and gives the scheduler a stable source key.  A
configuration entry is deliberately registered as ``candidate`` until an
official-ownership and public-access check has been recorded by an operator.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

from app.db import connect, init_db
from crawler.source_discovery import classify_ats


DEFAULT_SOURCE_FILE = Path("config/sources.json")

# These sources already have accepted, normalized jobs in the local database
# and have a dedicated adapter or a previously verified compatibility adapter.
# Keep this allowlist explicit: source discovery must never promote a source
# merely because a company or URL exists in the registry.
VERIFIED_SOURCE_KEYS = {
    "xiaomi-campus": "xiaomi_jobs_browser",
    "xiaopeng-campus": "feishu_jobs_browser",
    "papegames-campus": "papegames",
    "oppo-campus": "oppo",
    "mihoyo-campus": "mihoyo",
    "minimax-campus": "feishu_jobs_browser",
}

COMPANY_CANONICAL_ALIASES = {
    "小米集团": "小米",
    "小鹏集团": "小鹏",
    "oppo": "OPPO",
}


def _source_ats(source: dict) -> str:
    url = str(source.get("url") or "")
    if source.get("mode") == "feishu_jobs_browser":
        return "feishu"
    if source.get("mode") == "xiaomi_jobs_browser":
        return "feishu"
    return classify_ats(url)


def sync_config_sources(path: Path = DEFAULT_SOURCE_FILE) -> dict:
    """Upsert config entries into ``career_sources`` conservatively.

    Existing operator decisions (confirmed, blocked, paused, schedules) are
    preserved.  This function never creates jobs and never marks a source as
    confirmed or integrated.
    """
    init_db()
    sources = json.loads(path.read_text(encoding="utf-8"))
    created = updated = 0
    with connect() as conn:
        for source in sources:
            key = str(source.get("id") or "").strip()
            url = str(source.get("url") or "").strip()
            company = str(source.get("company") or "").strip()
            if not key or not url or not company:
                raise ValueError("config source requires id, company and url")
            canonical_company = COMPANY_CANONICAL_ALIASES.get(company, company)
            company_row = conn.execute(
                "SELECT id FROM companies WHERE canonical_name=?", (canonical_company,)
            ).fetchone()
            if company_row:
                company_id = company_row[0]
            else:
                company_id = conn.execute(
                    "INSERT INTO companies(canonical_name, brand_name) VALUES (?, ?)",
                    (canonical_company, canonical_company),
                ).lastrowid
            for alias in {company, canonical_company}:
                conn.execute(
                    "INSERT OR IGNORE INTO company_aliases(company_id, alias) VALUES (?, ?)",
                    (company_id, alias),
                )
            existing = conn.execute(
                "SELECT id, source_key FROM career_sources WHERE source_key=?", (key,)
            ).fetchone()
            # The workbook importer may already have registered the same URL
            # under a generated key.  Reuse that row instead of violating the
            # URL identity constraint or creating two schedulable records.
            if not existing:
                existing = conn.execute(
                    "SELECT id, source_key FROM career_sources WHERE url=?", (url,)
                ).fetchone()
            old_key = existing[1] if existing else None
            adapter = str(source.get("adapter") or source.get("mode") or "legacy")
            config = {
                k: source[k]
                for k in ("mode", "max_pages", "max_jobs", "page_delay_ms", "job_delay_ms", "snapshot_complete")
                if k in source
            }
            if existing:
                conn.execute(
                    """UPDATE career_sources
                       SET source_key=?, company_id=?, source_name=?, url=?, final_url=?, domain=?,
                           ats_type=?, adapter=?, adapter_config_json=?, updated_at=CURRENT_TIMESTAMP
                       WHERE source_key=?""",
                    (
                        key,
                        company_id,
                        str(source.get("name") or f"{company}招聘"),
                        url,
                        url,
                        urlsplit(url).netloc.lower(),
                        _source_ats(source),
                        adapter,
                        json.dumps(config, ensure_ascii=False, sort_keys=True),
                        old_key,
                    ),
                )
                updated += 1
            else:
                conn.execute(
                    """INSERT INTO career_sources(
                       source_key, company_id, source_name, url, final_url, domain,
                       recruitment_scope, ats_type, official_status, access_status,
                       integration_status, discovery_source, adapter, adapter_config_json,
                       enabled, quality_level, integration_priority
                    ) VALUES (?, ?, ?, ?, ?, ?, 'campus', ?, 'candidate', 'unknown',
                              'analyzing', 'config/sources.json', ?, ?, 1, 'low', 3)""",
                    (
                        key,
                        company_id,
                        str(source.get("name") or f"{company}招聘"),
                        url,
                        url,
                        urlsplit(url).netloc.lower(),
                        _source_ats(source),
                        adapter,
                        json.dumps(config, ensure_ascii=False, sort_keys=True),
                    ),
                )
                created += 1
    return {"created": created, "updated": updated, "sources": len(sources), "jobs_created": 0}


def reconcile_company_registry() -> dict:
    """Merge only explicit company aliases without deleting data."""
    init_db()
    merged: list[dict[str, str]] = []
    with connect() as conn:
        for alias, canonical in COMPANY_CANONICAL_ALIASES.items():
            target = conn.execute(
                "SELECT id FROM companies WHERE canonical_name=? AND status='active' LIMIT 1",
                (canonical,),
            ).fetchone()
            duplicate = conn.execute(
                "SELECT id FROM companies WHERE canonical_name=? AND status='active' LIMIT 1",
                (alias,),
            ).fetchone()
            if not target or not duplicate or target[0] == duplicate[0]:
                continue
            target_id, duplicate_id = target[0], duplicate[0]
            conn.execute("UPDATE career_sources SET company_id=? WHERE company_id=?", (target_id, duplicate_id))
            conn.execute(
                "UPDATE jobs SET company_id=?, company=? WHERE company_id=?",
                (target_id, canonical, duplicate_id),
            )
            conn.execute(
                "INSERT OR IGNORE INTO company_aliases(company_id, alias) VALUES (?, ?)",
                (target_id, alias),
            )
            conn.execute(
                "UPDATE companies SET status='merged', updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (duplicate_id,),
            )
            merged.append({"alias": alias, "canonical": canonical})
    return {"merged": merged}


def promote_verified_sources() -> dict:
    """Reconcile the registry with already verified local job integrations.

    This is an explicit operator migration, not part of normal config sync.
    It only promotes allowlisted adapters that have at least one active job
    and are not paused.  It never creates jobs and never touches candidates.
    """
    init_db()
    promoted: list[str] = []
    skipped: list[str] = []
    with connect() as conn:
        for source_key, adapter in VERIFIED_SOURCE_KEYS.items():
            row = conn.execute(
                """SELECT s.id, s.adapter, s.paused_reason,
                          COUNT(j.id) AS active_job_count
                   FROM career_sources s
                   LEFT JOIN jobs j ON j.source_id=s.source_key AND j.status='active'
                   WHERE s.source_key=?
                   GROUP BY s.id""",
                (source_key,),
            ).fetchone()
            if not row or row[1] != adapter or row[2] or int(row[3] or 0) < 1:
                skipped.append(source_key)
                continue
            conn.execute(
                """UPDATE career_sources
                   SET official_status='confirmed', access_status='reachable',
                       integration_status='integrated', quality_level='high',
                       integration_priority=0, updated_at=CURRENT_TIMESTAMP
                   WHERE id=?""",
                (row[0],),
            )
            promoted.append(source_key)
    return {"promoted": promoted, "skipped": skipped}


def main() -> None:
    parser = argparse.ArgumentParser(description="Register config sources without enabling collection")
    parser.add_argument("--source-file", type=Path, default=DEFAULT_SOURCE_FILE)
    parser.add_argument("--promote-verified", action="store_true")
    parser.add_argument("--reconcile-companies", action="store_true")
    args = parser.parse_args()
    result = sync_config_sources(args.source_file)
    if args.reconcile_companies:
        result["company_reconciliation"] = reconcile_company_registry()
    if args.promote_verified:
        result["verification_reconciliation"] = promote_verified_sources()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
