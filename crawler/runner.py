from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
import traceback

from app.db import (
    init_db,
    connect,
    upsert_job,
    deactivate_missing_jobs,
    record_source_snapshot,
    record_job_quarantine,
    snapshot_protection,
    crawl_cooldown_remaining,
)
from crawler.adapters import default_registry
from crawler.normalize import normalize_job
from crawler.normalize import JOB_NATURE_VALUES

SOURCE_FILE = Path("config/sources.json")


def is_qualified_job(job: dict) -> bool:
    """Enforce the concrete-position gate before a crawl can mutate job state."""
    has_detail = bool(str(job.get("description") or "").strip() or str(job.get("requirements") or "").strip())
    return (
        all(
            bool(str(job.get(field) or "").strip())
            for field in ("title", "city", "category", "degree", "job_nature", "apply_url", "source_url", "content_hash")
        )
        and has_detail
        and job.get("job_nature") in JOB_NATURE_VALUES
    )


def load_sources():
    sources = json.loads(SOURCE_FILE.read_text(encoding="utf-8"))
    for source in sources:
        # ``source_key`` is the stable identity used by career_sources and
        # by the scheduler; legacy job rows continue to use the config id.
        source.setdefault("source_key", source.get("id"))
        source.setdefault("adapter", source.get("mode") or "legacy")
    return sources


async def crawl_source(source: dict) -> dict:
    init_db()
    minimum_seconds = int(os.getenv("CRAWL_MIN_INTERVAL_SECONDS", "3600"))
    remaining = crawl_cooldown_remaining(source["id"], minimum_seconds)
    if remaining:
        return {
            "source_id": source["id"],
            "company": source["company"],
            "error": "crawl_cooldown_active",
            "cooldown_remaining_seconds": remaining,
        }
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO crawl_runs(source_id, status) VALUES (?, 'running')",
            (source["id"],),
        )
        run_id = cur.lastrowid

    created = updated = deactivated = 0
    protected = False
    protection_reason = None
    stop_reason = None
    with connect() as conn:
        previous_active_count = conn.execute(
            "SELECT COUNT(*) FROM jobs WHERE source_id=? AND status='active'",
            (source["id"],),
        ).fetchone()[0]
    try:
        adapter_name = source.get("adapter") or source.get("mode") or "legacy"
        adapter = default_registry().get(adapter_name)
        collection = await adapter.fetch_listing(source)
        stop_reason = collection.stop_reason
        if collection.stop_reason:
            raise RuntimeError(collection.stop_reason)
        response_urls = collection.response_urls
        normalized = []
        for item in collection.listing_items:
            raw = await adapter.fetch_detail(source, item)
            job = adapter.normalize(source, raw)
            if job:
                if is_qualified_job(job):
                    normalized.append(job)
                else:
                    record_job_quarantine(
                        source["id"], item.source_job_id, item.title,
                        "quality_gate_rejected", raw,
                    )
            else:
                record_job_quarantine(
                    source["id"], item.source_job_id, item.title,
                    "normalization_rejected", raw,
                )

        if not normalized:
            raise ValueError("crawl_produced_no_qualified_concrete_jobs")

        # Deduplicate normalized jobs by content hash.
        unique = {j["content_hash"]: j for j in normalized}
        for job in unique.values():
            result = upsert_job(job)
            created += result == "created"
            updated += result == "updated"

        snapshot_complete = bool(source.get("snapshot_complete") or collection.snapshot_complete)
        if snapshot_complete:
            protected, protection_reason, _ = snapshot_protection(source["id"], len(unique))
        if snapshot_complete and unique and not protected:
            deactivated = deactivate_missing_jobs(source["id"], unique.keys())

        content_hash = hashlib.sha256(
            "|".join(sorted(unique)).encode("utf-8", "ignore")
        ).hexdigest() if unique else None
        record_source_snapshot(
            source["id"],
            "success",
                len(collection.listing_items),
            len(unique),
            previous_active_count,
            protected,
            protection_reason,
            content_hash,
        )

        with connect() as conn:
            conn.execute(
                """
                UPDATE crawl_runs
                SET finished_at=CURRENT_TIMESTAMP, status='success',
                    jobs_found=?, jobs_created=?, jobs_updated=?
                WHERE id=?
                """,
                (len(unique), created, updated, run_id),
            )

        return {
            "source_id": source["id"],
            "company": source["company"],
            "jobs_found": len(unique),
            "created": created,
            "updated": updated,
            "deactivated": deactivated,
            "snapshot_protected": protected,
            "protection_reason": protection_reason,
            "json_endpoints_seen": response_urls[:50],
            "stop_reason": None,
        }
    except Exception as exc:
        record_source_snapshot(
            source["id"], "failed", 0, 0, previous_active_count, True, "crawl_failed"
        )
        with connect() as conn:
            conn.execute(
                """
                UPDATE crawl_runs
                SET finished_at=CURRENT_TIMESTAMP, status='failed', error_message=?
                WHERE id=?
                """,
                (f"{type(exc).__name__}: {exc}", run_id),
            )
        return {
            "source_id": source["id"],
            "company": source["company"],
            "error": str(exc),
            "stop_reason": stop_reason or (str(exc) if str(exc) in {
                "http_403", "http_429", "captcha", "security_verification",
                "verification_page_detected", "login_wall",
            } else None),
            "traceback": traceback.format_exc(limit=3),
        }


async def main_async(source_id: str | None):
    sources = [s for s in load_sources() if s.get("enabled", True)]
    if source_id:
        sources = [s for s in sources if s["id"] == source_id]
        if not sources:
            raise SystemExit(f"Unknown source id: {source_id}")

    results = []
    # Sequential by default so we do not hammer public recruitment sites.
    for source in sources:
        print(f"[crawl] {source['company']} -> {source['url']}")
        result = await crawl_source(source)
        results.append(result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", help="crawl one source id")
    args = parser.parse_args()
    asyncio.run(main_async(args.source))


if __name__ == "__main__":
    main()
