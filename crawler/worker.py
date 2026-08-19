"""Controlled one-source worker entry point.

It deliberately processes one configured source at a time and delegates
cooldown, stop signals, normalization and quality gates to the existing
runner. It never bypasses access controls.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import uuid

from app.db import acquire_crawl_lock, connect, init_db, release_crawl_lock
from crawler.runner import crawl_source, load_sources


async def run_one(source_id: str, update_schedule: bool = False) -> dict:
    init_db()
    source = next(
        (item for item in load_sources() if item["id"] == source_id or item.get("source_key") == source_id),
        None,
    )
    # Scheduler rows use the database source_key.  Keep the configured
    # source id as the job identity when available, while accepting a
    # source_key so the scheduler and one-shot worker share one contract.
    if not source:
        raise ValueError(f"unknown_source:{source_id}")
    owner = f"worker-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    if not acquire_crawl_lock(source_id, owner):
        return {"source_id": source_id, "accepted": False, "error": "source_locked"}
    try:
        result = await crawl_source(source)
        wrapped = {"source_id": source_id, "accepted": True, "result": result}
        if update_schedule:
            from crawler.scheduler import record_scheduler_result
            with connect() as conn:
                source_row = conn.execute(
                    "SELECT id FROM career_sources WHERE source_key=? OR CAST(id AS TEXT)=? LIMIT 1",
                    (source_id, source_id),
                ).fetchone()
            if source_row:
                record_scheduler_result(
                    source_row[0],
                    not bool(result.get("error")),
                    result.get("stop_reason"),
                )
        return wrapped
    finally:
        release_crawl_lock(source_id, owner)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one controlled recruitment source update")
    parser.add_argument("--source", required=True)
    args = parser.parse_args()
    print(asyncio.run(run_one(args.source, update_schedule=True)))


if __name__ == "__main__":
    main()
