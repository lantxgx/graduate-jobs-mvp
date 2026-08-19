from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime, timedelta, timezone

from app.db import connect, init_db
from crawler.worker import run_one


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def select_due_sources(limit: int = 1, now: datetime | None = None) -> list[dict]:
    init_db()
    current = (now or _now()).isoformat(sep=" ")
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT s.id, s.source_key, s.url, s.adapter, s.update_interval_seconds,
                   s.consecutive_failures, s.next_run_at, s.company_id,
                   c.canonical_name AS company_name
            FROM career_sources s
            JOIN companies c ON c.id=s.company_id
            WHERE s.enabled=1
              AND s.official_status='confirmed'
              AND s.access_status='reachable'
              AND s.integration_status='integrated'
              AND (s.paused_reason IS NULL OR TRIM(s.paused_reason)='')
              AND (s.next_run_at IS NULL OR s.next_run_at <= ?)
            ORDER BY COALESCE(s.next_run_at, ''), s.integration_priority, s.id
            LIMIT ?
            """,
            (current, min(max(limit, 1), 20)),
        ).fetchall()
    return [dict(row) for row in rows]


def record_scheduler_result(source_id: int, succeeded: bool, stop_reason: str | None = None) -> None:
    now = _now()
    with connect() as conn:
        row = conn.execute(
            "SELECT update_interval_seconds, consecutive_failures FROM career_sources WHERE id=?",
            (source_id,),
        ).fetchone()
        if not row:
            return
        interval = int(row[0] or 43200)
        failures = int(row[1] or 0)
        if succeeded:
            conn.execute(
                """UPDATE career_sources
                   SET last_attempt_at=?, last_success_at=?, consecutive_failures=0,
                       next_run_at=?, paused_reason=NULL, updated_at=CURRENT_TIMESTAMP
                   WHERE id=?""",
                (now.isoformat(sep=" "), now.isoformat(sep=" "), (now + timedelta(seconds=interval)).isoformat(sep=" "), source_id),
            )
        elif stop_reason in {
            "http_403", "http_429", "captcha", "security_verification",
            "verification_page_detected", "login_wall",
        }:
            conn.execute(
                """UPDATE career_sources
                   SET last_attempt_at=?, consecutive_failures=?, next_run_at=NULL,
                       paused_reason=?, updated_at=CURRENT_TIMESTAMP
                   WHERE id=?""",
                (now.isoformat(sep=" "), failures + 1, stop_reason, source_id),
            )
        else:
            backoff = min(24 * 3600, 3600 * (2 ** min(failures, 3)))
            conn.execute(
                """UPDATE career_sources
                   SET last_attempt_at=?, consecutive_failures=?, next_run_at=?, updated_at=CURRENT_TIMESTAMP
                   WHERE id=?""",
                (now.isoformat(sep=" "), failures + 1, (now + timedelta(seconds=backoff)).isoformat(sep=" "), source_id),
            )


async def run_once() -> list[dict]:
    results = []
    for source in select_due_sources(limit=1):
        result = await run_one(source["source_key"], update_schedule=False)
        results.append(result)
        nested = result.get("result") or {}
        stop_reason = nested.get("stop_reason")
        succeeded = not bool(nested.get("error"))
        record_scheduler_result(source["id"], succeeded, stop_reason)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one low-frequency recruitment source update")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--loop", action="store_true")
    args = parser.parse_args()
    if not args.once and not args.loop:
        parser.error("choose --once or --loop")
    if args.once:
        print(json.dumps(asyncio.run(run_once()), ensure_ascii=False, default=str), flush=True)
        return
    while True:
        result = asyncio.run(run_once())
        print(json.dumps({"event": "scheduler_poll", "results": result}, ensure_ascii=False, default=str), flush=True)
        asyncio.run(asyncio.sleep(60))


if __name__ == "__main__":
    main()
