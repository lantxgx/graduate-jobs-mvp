from __future__ import annotations

import json
import hashlib
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, Any

from app.taxonomy import classify_job

DB_PATH = Path(os.getenv("DATABASE_PATH", "data/jobs.db"))


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT NOT NULL,
                source_job_id TEXT,
                company TEXT NOT NULL,
                title TEXT NOT NULL,
                city TEXT,
                job_nature TEXT,
                category TEXT,
                degree TEXT,
                graduate_year TEXT,
                requirements TEXT,
                description TEXT,
                apply_url TEXT,
                source_url TEXT NOT NULL,
                published_at TEXT,
                first_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL DEFAULT 'active',
                content_hash TEXT NOT NULL,
                raw_json TEXT,
                job_family TEXT,
                job_family_confidence REAL,
                job_family_evidence TEXT,
                company_id INTEGER,
                detail_hash TEXT,
                listing_hash TEXT,
                detail_fetched_at TEXT,
                missing_snapshot_count INTEGER NOT NULL DEFAULT 0,
                last_changed_at TEXT,
                UNIQUE(source_id, content_hash)
            );

            CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
            CREATE INDEX IF NOT EXISTS idx_jobs_city ON jobs(city);
            CREATE INDEX IF NOT EXISTS idx_jobs_category ON jobs(category);
            CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);

            CREATE TABLE IF NOT EXISTS crawl_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT NOT NULL,
                started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                finished_at TEXT,
                status TEXT NOT NULL DEFAULT 'running',
                jobs_found INTEGER NOT NULL DEFAULT 0,
                jobs_created INTEGER NOT NULL DEFAULT 0,
                jobs_updated INTEGER NOT NULL DEFAULT 0,
                error_message TEXT
            );

            CREATE TABLE IF NOT EXISTS source_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT NOT NULL,
                captured_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL,
                discovered_count INTEGER NOT NULL DEFAULT 0,
                qualified_count INTEGER NOT NULL DEFAULT 0,
                previous_active_count INTEGER NOT NULL DEFAULT 0,
                protected INTEGER NOT NULL DEFAULT 0,
                protection_reason TEXT,
                content_hash TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_source_snapshots_source
                ON source_snapshots(source_id, id DESC);

            CREATE TABLE IF NOT EXISTS job_quarantine (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT NOT NULL,
                source_job_id TEXT NOT NULL,
                title TEXT,
                reason TEXT NOT NULL,
                raw_json TEXT,
                first_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(source_id, source_job_id, reason)
            );

            CREATE INDEX IF NOT EXISTS idx_job_quarantine_source
                ON job_quarantine(source_id, id DESC);

            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                canonical_name TEXT NOT NULL UNIQUE,
                brand_name TEXT,
                official_website TEXT,
                official_domain TEXT,
                status TEXT NOT NULL DEFAULT 'active',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS company_aliases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                alias TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id)
            );

            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_key TEXT NOT NULL UNIQUE,
                profile_json TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS job_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(job_id, action),
                FOREIGN KEY(job_id) REFERENCES jobs(id)
            );

            CREATE TABLE IF NOT EXISTS crawl_locks (
                source_id TEXT PRIMARY KEY,
                owner TEXT NOT NULL,
                acquired_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS career_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_key TEXT NOT NULL UNIQUE,
                company_id INTEGER NOT NULL,
                source_name TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                final_url TEXT,
                domain TEXT,
                recruitment_scope TEXT NOT NULL DEFAULT 'unknown',
                ats_type TEXT NOT NULL DEFAULT 'unknown',
                official_status TEXT NOT NULL DEFAULT 'unverified',
                access_status TEXT NOT NULL DEFAULT 'unknown',
                integration_status TEXT NOT NULL DEFAULT 'not_integrated',
                evidence_url TEXT,
                discovery_source TEXT,
                covered_cohorts TEXT,
                source_category TEXT,
                http_status INTEGER,
                page_title TEXT,
                last_verified_at TEXT,
                notes TEXT,
                raw_json TEXT,
                enabled INTEGER NOT NULL DEFAULT 1,
                quality_level TEXT NOT NULL DEFAULT 'low',
                integration_priority INTEGER NOT NULL DEFAULT 4,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id)
            );

            CREATE INDEX IF NOT EXISTS idx_career_sources_company ON career_sources(company_id);
            CREATE INDEX IF NOT EXISTS idx_career_sources_ats ON career_sources(ats_type);
            CREATE INDEX IF NOT EXISTS idx_career_sources_official ON career_sources(official_status);
            CREATE INDEX IF NOT EXISTS idx_career_sources_access ON career_sources(access_status);
            CREATE INDEX IF NOT EXISTS idx_career_sources_integration ON career_sources(integration_status);
            """
        )
        # Keep the migration lightweight for the existing MVP database.
        columns = {row[1] for row in conn.execute("PRAGMA table_info(career_sources)").fetchall()}
        if "quality_level" not in columns:
            conn.execute("ALTER TABLE career_sources ADD COLUMN quality_level TEXT NOT NULL DEFAULT 'low'")
        if "integration_priority" not in columns:
            conn.execute(
                "ALTER TABLE career_sources ADD COLUMN integration_priority INTEGER NOT NULL DEFAULT 4"
            )
        for column, definition in (
            ("adapter", "TEXT"),
            ("adapter_config_json", "TEXT"),
            ("update_interval_seconds", "INTEGER NOT NULL DEFAULT 43200"),
            ("next_run_at", "TEXT"),
            ("last_attempt_at", "TEXT"),
            ("last_success_at", "TEXT"),
            ("consecutive_failures", "INTEGER NOT NULL DEFAULT 0"),
            ("paused_reason", "TEXT"),
        ):
            if column not in columns:
                conn.execute(f"ALTER TABLE career_sources ADD COLUMN {column} {definition}")
        job_columns = {row[1] for row in conn.execute("PRAGMA table_info(jobs)").fetchall()}
        if "job_family" not in job_columns:
            conn.execute("ALTER TABLE jobs ADD COLUMN job_family TEXT")
        if "job_family_confidence" not in job_columns:
            conn.execute("ALTER TABLE jobs ADD COLUMN job_family_confidence REAL")
        if "job_family_evidence" not in job_columns:
            conn.execute("ALTER TABLE jobs ADD COLUMN job_family_evidence TEXT")
        for column, definition in (
            ("company_id", "INTEGER"),
            ("detail_hash", "TEXT"),
            ("listing_hash", "TEXT"),
            ("detail_fetched_at", "TEXT"),
            ("missing_snapshot_count", "INTEGER NOT NULL DEFAULT 0"),
            ("last_changed_at", "TEXT"),
        ):
            if column not in job_columns:
                conn.execute(f"ALTER TABLE jobs ADD COLUMN {column} {definition}")

        # Seed canonical and brand aliases, then reconcile known source naming variants.
        companies = conn.execute(
            "SELECT id, canonical_name, brand_name FROM companies WHERE status='active'"
        ).fetchall()
        for company in companies:
            for alias in (company[1], company[2]):
                if alias:
                    conn.execute(
                        "INSERT OR IGNORE INTO company_aliases(company_id, alias) VALUES (?, ?)",
                        (company[0], alias),
                    )
        for alias, canonical in (("小米集团", "小米"), ("小鹏集团", "小鹏")):
            company = conn.execute(
                "SELECT id FROM companies WHERE canonical_name=? LIMIT 1", (canonical,)
            ).fetchone()
            if company:
                conn.execute(
                    "INSERT OR IGNORE INTO company_aliases(company_id, alias) VALUES (?, ?)",
                    (company[0], alias),
                )
        conn.execute(
            """UPDATE jobs SET company_id=(
                SELECT company_id FROM company_aliases a WHERE a.alias=jobs.company LIMIT 1
            ) WHERE company_id IS NULL"""
        )
        conn.execute(
            """UPDATE jobs SET company=(
                SELECT c.canonical_name FROM companies c WHERE c.id=jobs.company_id
            ) WHERE company_id IS NOT NULL"""
        )

        # Normalize legacy free-text fields without removing any rows.
        from crawler.normalize import normalize_category, normalize_degree, normalize_job_nature
        for row in conn.execute(
            "SELECT id, title, job_nature, category, degree, requirements, description, status FROM jobs"
        ).fetchall():
            nature = normalize_job_nature(row[2], row[1], " ".join(filter(None, (row[5], row[6]))))
            category = normalize_category(row[3], row[1], " ".join(filter(None, (row[5], row[6]))))
            degree = normalize_degree(row[4], row[5] or "")
            status = row[7]
            if status == "active" and not nature:
                status = "quarantined"
            conn.execute(
                "UPDATE jobs SET job_nature=?, category=?, degree=?, status=? WHERE id=?",
                (nature, category, degree, status, row[0]),
            )

        # Reconcile source-specific authoritative taxonomy when a provider's
        # broad category labels changed after the original crawl.  This keeps
        # already stored observations consistent without contacting the source
        # again; the raw public payload is the only input to the migration.
        try:
            from crawler.adapters.mihoyo import normalize_mihoyo_job

            mihoyo_rows = conn.execute(
                "SELECT id, source_id, company, source_url, raw_json FROM jobs "
                "WHERE source_id='mihoyo-campus' AND raw_json IS NOT NULL"
            ).fetchall()
            for row in mihoyo_rows:
                try:
                    raw = json.loads(row[4])
                    normalized = normalize_mihoyo_job(
                        raw,
                        {"id": row[1], "company": row[2], "url": row[3]},
                    )
                except (TypeError, ValueError, json.JSONDecodeError):
                    normalized = None
                if normalized:
                    conn.execute(
                        "UPDATE jobs SET category=?, job_family=NULL, "
                        "job_family_confidence=NULL, job_family_evidence=NULL WHERE id=?",
                        (normalized.get("category"), row[0]),
                    )
        except ImportError:
            # Keep database initialization independent of optional adapters.
            pass

        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_source_job_identity "
            "ON jobs(source_id, source_job_id) "
            "WHERE status='active' AND source_job_id IS NOT NULL AND TRIM(source_job_id) <> ''"
        )
        for row in conn.execute(
            "SELECT id, title, category, description FROM jobs"
        ).fetchall():
            family, confidence, evidence = classify_job(row[1], row[2], row[3])
            conn.execute(
                "UPDATE jobs SET job_family=?, job_family_confidence=?, job_family_evidence=? WHERE id=?",
                (family, confidence, json.dumps(evidence, ensure_ascii=False), row[0]),
            )


@contextmanager
def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def upsert_job(job: dict[str, Any]) -> str:
    from crawler.normalize import normalize_category, normalize_degree, normalize_job_nature

    job = dict(job)
    job["job_nature"] = normalize_job_nature(
        job.get("job_nature"), job.get("title", ""),
        " ".join(filter(None, (job.get("description"), job.get("requirements"))))
    )
    if job["job_nature"] is None:
        raise ValueError("unsupported_or_unknown_job_nature")
    job["category"] = normalize_category(
        job.get("category"), job.get("title", ""),
        " ".join(filter(None, (job.get("description"), job.get("requirements"))))
    )
    job["degree"] = normalize_degree(job.get("degree"), job.get("requirements") or "")
    family, confidence, evidence = classify_job(
        job.get("title"), job.get("category"), job.get("description")
    )
    detail_hash = job.get("detail_hash") or hashlib.sha256(
        "|".join(str(job.get(key) or "") for key in ("title", "description", "requirements", "degree")).encode(
            "utf-8", "ignore"
        )
    ).hexdigest()
    with connect() as conn:
        existing = None
        if job.get("source_job_id"):
            existing = conn.execute(
                "SELECT id FROM jobs WHERE source_id=? AND source_job_id=? ORDER BY id LIMIT 1",
                (job["source_id"], job["source_job_id"]),
            ).fetchone()
        if not existing:
            existing = conn.execute(
                "SELECT id FROM jobs WHERE source_id=? AND content_hash=? ORDER BY id LIMIT 1",
                (job["source_id"], job["content_hash"]),
            ).fetchone()

        company_id_row = conn.execute(
            "SELECT company_id FROM company_aliases WHERE alias=? LIMIT 1",
            (job.get("company"),),
        ).fetchone()
        company_id = company_id_row[0] if company_id_row else None
        if company_id:
            canonical = conn.execute(
                "SELECT canonical_name FROM companies WHERE id=?", (company_id,)
            ).fetchone()
            if canonical:
                job["company"] = canonical[0]

        if existing:
            conn.execute(
                """
                UPDATE jobs
                SET company=?,
                    company_id=?,
                    last_seen_at=CURRENT_TIMESTAMP,
                    status='active',
                    source_job_id=?,
                    content_hash=?,
                    detail_hash=?,
                    detail_fetched_at=CURRENT_TIMESTAMP,
                    missing_snapshot_count=0,
                    last_changed_at=CASE WHEN COALESCE(detail_hash,'') <> ?
                                         THEN CURRENT_TIMESTAMP ELSE last_changed_at END,
                    city=?,
                    job_nature=?,
                    category=?,
                    degree=?,
                    graduate_year=?,
                    requirements=?,
                    description=?,
                    apply_url=?,
                    published_at=?,
                    raw_json=?,
                    job_family=?,
                    job_family_confidence=?,
                    job_family_evidence=?
                WHERE id=?
                """,
                (
                    job["company"],
                    company_id,
                    job.get("source_job_id"),
                    job["content_hash"],
                    detail_hash,
                    detail_hash,
                    job.get("city"),
                    job.get("job_nature"),
                    job.get("category"),
                    job.get("degree"),
                    job.get("graduate_year"),
                    job.get("requirements"),
                    job.get("description"),
                    job.get("apply_url"),
                    job.get("published_at"),
                    json.dumps(job.get("raw", {}), ensure_ascii=False),
                    family,
                    confidence,
                    json.dumps(evidence, ensure_ascii=False),
                    existing["id"],
                ),
            )
            return "updated"

        conn.execute(
            """
            INSERT INTO jobs (
                source_id, source_job_id, company, company_id, title, city, job_nature,
                category, degree, graduate_year, requirements, description,
                apply_url, source_url, published_at, content_hash, raw_json,
                job_family, job_family_confidence, job_family_evidence,
                detail_hash, detail_fetched_at, last_changed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job["source_id"],
                job.get("source_job_id"),
                job["company"],
                company_id,
                job["title"],
                job.get("city"),
                job.get("job_nature"),
                job.get("category"),
                job.get("degree"),
                job.get("graduate_year"),
                job.get("requirements"),
                job.get("description"),
                job.get("apply_url"),
                job["source_url"],
                job.get("published_at"),
                job["content_hash"],
                json.dumps(job.get("raw", {}), ensure_ascii=False),
                family,
                confidence,
                json.dumps(evidence, ensure_ascii=False),
                detail_hash,
                None,
                None,
            ),
        )
        return "created"


def record_job_quarantine(
    source_id: str,
    source_job_id: str | None,
    title: str | None,
    reason: str,
    raw: Any = None,
) -> None:
    """Preserve a rejected public job observation without exposing it as active."""
    init_db()
    stable_id = str(source_job_id or title or "unknown").strip() or "unknown"
    with connect() as conn:
        conn.execute(
            """INSERT INTO job_quarantine(source_id, source_job_id, title, reason, raw_json)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(source_id, source_job_id, reason)
               DO UPDATE SET title=excluded.title, raw_json=excluded.raw_json,
                             last_seen_at=CURRENT_TIMESTAMP""",
            (source_id, stable_id, title, reason, json.dumps(raw, ensure_ascii=False, default=str)),
        )


def query_job_quarantine(source_id: str = "", limit: int = 100) -> list[dict]:
    init_db()
    clauses = ["1=1"]
    params: list[Any] = []
    if source_id:
        clauses.append("source_id=?")
        params.append(source_id)
    params.append(min(max(limit, 1), 500))
    with connect() as conn:
        rows = conn.execute(
            f"""SELECT q.id, q.source_id, q.source_job_id, q.title, q.reason, q.raw_json,
                       q.first_seen_at, q.last_seen_at,
                       c.canonical_name AS company_name, s.source_name
                FROM job_quarantine q
                LEFT JOIN career_sources s ON s.source_key=q.source_id OR CAST(s.id AS TEXT)=q.source_id
                LEFT JOIN companies c ON c.id=s.company_id
                WHERE {' AND '.join('q.' + clause if clause != '1=1' else clause for clause in clauses)}
                ORDER BY q.last_seen_at DESC, q.id DESC LIMIT ?""",
            params,
        ).fetchall()
    return [dict(row) for row in rows]


def deactivate_missing_jobs(source_id: str, active_hashes: Iterable[str]) -> int:
    """Mark records absent from a complete source snapshot as inactive."""
    hashes = list(dict.fromkeys(active_hashes))
    if not hashes:
        return 0
    with connect() as conn:
        conn.execute(
            "CREATE TEMP TABLE IF NOT EXISTS active_job_hashes "
            "(content_hash TEXT PRIMARY KEY)"
        )
        conn.execute("DELETE FROM active_job_hashes")
        conn.executemany(
            "INSERT OR IGNORE INTO active_job_hashes(content_hash) VALUES (?)",
            ((value,) for value in hashes),
        )
        conn.execute(
            """
            UPDATE jobs
            SET missing_snapshot_count=COALESCE(missing_snapshot_count, 0) + 1
            WHERE source_id=? AND status='active'
              AND NOT EXISTS (
                  SELECT 1 FROM active_job_hashes active
                  WHERE active.content_hash=jobs.content_hash
              )
            """,
            (source_id,),
        )
        cursor = conn.execute(
            """UPDATE jobs SET status='inactive'
               WHERE source_id=? AND status='active'
                 AND missing_snapshot_count >= 3""",
            (source_id,),
        )
        return cursor.rowcount


def record_source_snapshot(
    source_id: str,
    status: str,
    discovered_count: int,
    qualified_count: int,
    previous_active_count: int,
    protected: bool = False,
    protection_reason: str | None = None,
    content_hash: str | None = None,
) -> int:
    with connect() as conn:
        cursor = conn.execute(
            """INSERT INTO source_snapshots(
                source_id, status, discovered_count, qualified_count, previous_active_count,
                protected, protection_reason, content_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                source_id,
                status,
                discovered_count,
                qualified_count,
                previous_active_count,
                int(protected),
                protection_reason,
                content_hash,
            ),
        )
        return cursor.lastrowid


def snapshot_protection(source_id: str, current_count: int) -> tuple[bool, str | None, int]:
    """Protect existing jobs when a new complete snapshot drops suspiciously."""
    with connect() as conn:
        previous = conn.execute(
            """SELECT qualified_count FROM source_snapshots
               WHERE source_id=? AND status='success' AND qualified_count > 0
               ORDER BY id DESC LIMIT 1""",
            (source_id,),
        ).fetchone()
    if current_count == 0:
        return True, "empty_snapshot", previous[0] if previous else 0
    if previous and current_count < max(1, int(previous[0] * 0.5)):
        return True, "sudden_drop_over_50_percent", previous[0]
    return False, None, previous[0] if previous else 0


def query_source_snapshots(source_id: str = "", limit: int = 50) -> list[dict]:
    clauses = []
    params: list[Any] = []
    if source_id:
        clauses.append("source_id=?")
        params.append(source_id)
    params.append(min(max(limit, 1), 200))
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    with connect() as conn:
        return [
            dict(row)
            for row in conn.execute(
                f"SELECT * FROM source_snapshots {where} ORDER BY id DESC LIMIT ?", params
            ).fetchall()
        ]


def get_user_profile(profile_key: str = "local") -> dict | None:
    init_db()
    with connect() as conn:
        row = conn.execute(
            "SELECT profile_json, created_at, updated_at FROM user_profiles WHERE profile_key=?",
            (profile_key,),
        ).fetchone()
    if not row:
        return None
    profile = json.loads(row[0])
    profile["created_at"] = row[1]
    profile["updated_at"] = row[2]
    return profile


def save_user_profile(profile: dict, profile_key: str = "local") -> dict:
    init_db()
    payload = json.dumps(profile, ensure_ascii=False, sort_keys=True)
    with connect() as conn:
        conn.execute(
            """INSERT INTO user_profiles(profile_key, profile_json)
               VALUES (?, ?)
               ON CONFLICT(profile_key) DO UPDATE SET
                 profile_json=excluded.profile_json, updated_at=CURRENT_TIMESTAMP""",
            (profile_key, payload),
        )
    return get_user_profile(profile_key) or profile


def delete_user_profile(profile_key: str = "local") -> bool:
    init_db()
    with connect() as conn:
        cursor = conn.execute("DELETE FROM user_profiles WHERE profile_key=?", (profile_key,))
        return cursor.rowcount > 0


def set_job_action(job_id: int, action: str, enabled: bool = True) -> bool:
    if action not in {"favorite", "ignore", "applied"}:
        raise ValueError("Unsupported job action")
    init_db()
    with connect() as conn:
        if enabled:
            conn.execute(
                "INSERT OR IGNORE INTO job_actions(job_id, action) VALUES (?, ?)",
                (job_id, action),
            )
        else:
            conn.execute("DELETE FROM job_actions WHERE job_id=? AND action=?", (job_id, action))
    return enabled


def query_job_actions(action: str = "") -> list[dict]:
    init_db()
    with connect() as conn:
        if action:
            return [dict(row) for row in conn.execute(
                "SELECT * FROM job_actions WHERE action=? ORDER BY id DESC", (action,)
            ).fetchall()]
        return [dict(row) for row in conn.execute("SELECT * FROM job_actions ORDER BY id DESC").fetchall()]


def query_job_updates(since: str = "", limit: int = 100) -> list[dict]:
    """Return active jobs first seen or materially changed after ``since``.

    ``last_changed_at`` is populated when a stable job identity receives new
    detail content; new rows fall back to ``first_seen_at``.  The endpoint is
    intentionally read-only so a UI refresh cannot trigger collection.
    """
    normalized_since = (since or "").strip().replace("T", " ")
    clauses = ["status='active'"]
    params: list[Any] = []
    if normalized_since:
        clauses.append("COALESCE(last_changed_at, first_seen_at) >= ?")
        params.append(normalized_since)
    params.append(min(max(limit, 1), 500))
    with connect() as conn:
        rows = conn.execute(
            f"""SELECT id, source_id, source_job_id, company, title, city,
                       category, job_nature, degree, apply_url, source_url,
                       first_seen_at, last_seen_at, last_changed_at,
                       COALESCE(last_changed_at, first_seen_at) AS update_time
                FROM jobs WHERE {' AND '.join(clauses)}
                ORDER BY update_time DESC, id DESC LIMIT ?""",
            params,
        ).fetchall()
    return [dict(row) for row in rows]
def crawl_cooldown_remaining(source_id: str, minimum_seconds: int = 3600) -> int:
    """Return remaining cooldown seconds; zero means a crawl may start."""
    with connect() as conn:
        row = conn.execute(
            """SELECT CAST((julianday('now') - julianday(started_at)) * 86400 AS INTEGER)
               FROM crawl_runs WHERE source_id=? ORDER BY id DESC LIMIT 1""",
            (source_id,),
        ).fetchone()
    if not row or row[0] is None:
        return 0
    return max(0, minimum_seconds - int(row[0]))


def acquire_crawl_lock(source_id: str, owner: str, stale_seconds: int = 7200) -> bool:
    """Claim one source for a bounded worker run; stale claims are recoverable."""
    with connect() as conn:
        row = conn.execute(
            "SELECT owner, (julianday('now') - julianday(acquired_at)) * 86400 FROM crawl_locks WHERE source_id=?",
            (source_id,),
        ).fetchone()
        if row and float(row[1] or 0) < stale_seconds:
            return False
        if row:
            conn.execute("DELETE FROM crawl_locks WHERE source_id=?", (source_id,))
        conn.execute("INSERT INTO crawl_locks(source_id, owner) VALUES (?, ?)", (source_id, owner))
        return True


def release_crawl_lock(source_id: str, owner: str) -> bool:
    with connect() as conn:
        cursor = conn.execute("DELETE FROM crawl_locks WHERE source_id=? AND owner=?", (source_id, owner))
        return cursor.rowcount > 0


def query_ingestion_queue(limit: int = 100) -> list[dict]:
    init_db()
    with connect() as conn:
        rows = conn.execute(
            """SELECT s.id, s.source_key, s.source_name, c.canonical_name AS company_name,
                      s.url, s.ats_type, s.adapter, s.official_status, s.access_status,
                      s.quality_level, s.integration_priority, s.integration_status,
                      s.last_attempt_at, s.last_success_at, s.next_run_at, s.paused_reason
               FROM career_sources s JOIN companies c ON c.id=s.company_id
               WHERE s.enabled=1
                 AND s.official_status IN ('confirmed', 'candidate')
                 AND s.access_status='reachable'
                 AND s.integration_status NOT IN ('integrated', 'excluded')
               ORDER BY s.integration_priority, s.quality_level, s.id
               LIMIT ?""",
            (min(max(limit, 1), 500),),
        ).fetchall()
    return [dict(row) for row in rows]


def query_jobs(
    keyword: str = "",
    company: str = "",
    city: str = "",
    category: str = "",
    job_nature: str = "",
    degree: str = "",
    limit: int = 100,
    job_family: str = "",
    offset: int = 0,
) -> list[dict]:
    clauses = ["status='active'"]
    params: list[Any] = []

    if keyword:
        clauses.append("(title LIKE ? OR description LIKE ? OR requirements LIKE ?)")
        q = f"%{keyword}%"
        params.extend([q, q, q])
    if company:
        clauses.append("company=?")
        params.append(company)
    if city:
        clauses.append("city LIKE ?")
        params.append(f"%{city}%")
    if category:
        clauses.append("category LIKE ?")
        params.append(f"%{category}%")
    if job_nature:
        clauses.append("job_nature LIKE ?")
        params.append(f"%{job_nature}%")
    if degree:
        clauses.append("degree LIKE ?")
        params.append(f"%{degree}%")
    if job_family:
        clauses.append("job_family=?")
        params.append(job_family)

    sql = f"""
        SELECT id, source_id, source_job_id, company, title, city, job_nature,
               category, degree, graduate_year, requirements, description,
               apply_url, source_url, published_at, first_seen_at, last_seen_at,
               job_family, job_family_confidence, job_family_evidence
        FROM jobs
        WHERE {' AND '.join(clauses)}
        ORDER BY last_seen_at DESC, COALESCE(published_at, first_seen_at) DESC
        LIMIT ? OFFSET ?
    """
    params.extend([min(max(limit, 1), 500), max(offset, 0)])
    with connect() as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


def count_jobs(
    keyword: str = "",
    company: str = "",
    city: str = "",
    category: str = "",
    job_nature: str = "",
    degree: str = "",
    job_family: str = "",
) -> int:
    clauses = ["status='active'"]
    params: list[Any] = []
    if keyword:
        clauses.append("(title LIKE ? OR description LIKE ? OR requirements LIKE ?)")
        q = f"%{keyword}%"
        params.extend([q, q, q])
    if company:
        clauses.append("company=?")
        params.append(company)
    if city:
        clauses.append("city LIKE ?")
        params.append(f"%{city}%")
    if category:
        clauses.append("category LIKE ?")
        params.append(f"%{category}%")
    if job_nature:
        clauses.append("job_nature LIKE ?")
        params.append(f"%{job_nature}%")
    if degree:
        clauses.append("degree LIKE ?")
        params.append(f"%{degree}%")
    if job_family:
        clauses.append("job_family=?")
        params.append(job_family)
    with connect() as conn:
        return int(conn.execute(f"SELECT COUNT(*) FROM jobs WHERE {' AND '.join(clauses)}", params).fetchone()[0])


def query_jobs_with_profile(
    profile: dict | None = None,
    keyword: str = "",
    company: str = "",
    city: str = "",
    category: str = "",
    job_nature: str = "",
    degree: str = "",
    limit: int = 100,
) -> list[dict]:
    """Return all matching jobs with explainable explicit hard-condition flags."""
    jobs = query_jobs(keyword, company, city, category, job_nature, degree, limit)
    profile = profile or {}
    excluded_roles = [str(value).lower() for value in profile.get("excluded_roles", [])]
    target_cities = [str(value).lower() for value in profile.get("target_cities", [])]
    city_mode = str(profile.get("city_preference_mode") or "preference").lower()
    target_companies = [str(value).lower() for value in profile.get("target_companies", [])]
    for job in jobs:
        text = " ".join(str(job.get(key) or "") for key in ("title", "category", "description")).lower()
        reasons: list[str] = []
        if excluded_roles and any(role and role in text for role in excluded_roles):
            reasons.append("explicitly_excluded_role")
        if city_mode == "hard" and target_cities and job.get("city"):
            job_city = str(job["city"]).lower()
            if not any(city_name in job_city for city_name in target_cities):
                reasons.append("outside_explicit_city_preference")
        job["explicit_target_company"] = bool(
            target_companies and any(name in str(job.get("company") or "").lower() for name in target_companies)
        )
        hard_reasons = {"explicitly_excluded_role"}
        if city_mode == "hard":
            hard_reasons.add("outside_explicit_city_preference")
        job["hard_filter_pass"] = not any(reason in hard_reasons for reason in reasons)
        job["hard_filter_reasons"] = reasons
    return jobs


def recommend_jobs(profile: dict | None = None, limit: int = 100) -> dict:
    """Build explainable recommendation pools without hiding the all-jobs view."""
    profile = profile or {}
    jobs = query_jobs_with_profile(profile, limit=500)
    targets = [str(value).lower() for value in profile.get("target_roles", [])]
    adjacent = [str(value).lower() for value in profile.get("adjacent_roles", [])]
    companies = [str(value).lower() for value in profile.get("target_companies", [])]
    skills = [str(value).lower() for value in profile.get("skills", [])]

    with connect() as conn:
        feedback_rows = conn.execute("SELECT job_id, action FROM job_actions").fetchall()
    feedback: dict[int, set[str]] = {}
    for row in feedback_rows:
        feedback.setdefault(int(row[0]), set()).add(str(row[1]))

    pools = {"main": [], "target_company": [], "adjacent": [], "exploration": []}
    for job in jobs:
        job_feedback = feedback.get(int(job["id"]), set())
        job["feedback_actions"] = sorted(job_feedback)
        # Ignore is a soft preference: all-jobs search remains complete, while
        # default recommendations stop resurfacing explicitly ignored jobs.
        if "ignore" in job_feedback:
            continue
        if not job.get("hard_filter_pass", True):
            continue
        text = " ".join(str(job.get(key) or "") for key in ("title", "category", "description")).lower()
        target_families = {classify_job(value, None, None)[0] for value in targets}
        adjacent_families = {classify_job(value, None, None)[0] for value in adjacent}
        is_main = any(value and value in text for value in targets) or bool(
            job.get("job_family") and job.get("job_family") in target_families
        )
        is_adjacent = any(value and value in text for value in adjacent) or bool(
            job.get("job_family") and job.get("job_family") in adjacent_families
        )
        is_target_company = bool(companies and any(value in str(job.get("company") or "").lower() for value in companies))
        matched_skills = [skill for skill in skills if skill and skill in text]
        recall_channels = []
        if any(value and value in text for value in targets):
            recall_channels.append("keyword_role")
        if job.get("job_family") and job.get("job_family") in target_families:
            recall_channels.append("job_family")
        if matched_skills:
            recall_channels.append("skill_evidence")
        if is_target_company:
            recall_channels.append("target_company")
        if is_adjacent:
            recall_channels.append("adjacent_role")
        if is_main:
            pool = "main"
        elif is_target_company:
            pool = "target_company"
        elif is_adjacent:
            pool = "adjacent"
        else:
            pool = "exploration"
        job["recommendation_pool"] = pool
        job["recommendation_reasons"] = {
            "target_role_match": is_main,
            "target_company_match": is_target_company,
            "adjacent_role_match": is_adjacent,
            "explicit_exclusion_applied": False,
        }
        job["match_dimensions"] = {
            "basic_qualification": _qualification_dimension(job, profile),
            "ability_match": {"status": "matched" if matched_skills else "unconfirmed", "evidence": matched_skills},
            "job_seeking_intent": {"status": "matched" if (is_main or is_adjacent) else "unconfirmed", "evidence": targets or adjacent},
            "company_preference": {"status": "matched" if is_target_company else "unconfirmed", "evidence": companies if is_target_company else []},
            "transition_distance": {"status": "adjacent" if is_adjacent and not is_main else ("direct" if is_main else "unknown"), "evidence": [job.get("job_family")] if job.get("job_family") else []},
            "confidence": {"status": "review", "evidence": job.get("job_family_evidence") or []},
            "role_family_match": is_main,
            "skill_matches": matched_skills,
            "target_company_match": is_target_company,
            "adjacent_role_match": is_adjacent,
        }
        job["recall_channels"] = recall_channels
        job["explainable_score"] = (
            (35 if is_main else 0)
            + min(25, len(matched_skills) * 5)
            + (25 if is_target_company else 0)
            + (15 if is_adjacent else 0)
        )
        job["adjacent_explanation"] = _adjacent_explanation(job, profile) if is_adjacent else None
        job["competition_risk"], job["competition_risk_basis"] = _competition_risk(job)
        pools[pool].append(job)

    for values in pools.values():
        values.sort(key=lambda item: (item.get("explainable_score", 0), item.get("last_seen_at") or ""), reverse=True)

    configured_mix = profile.get("recommendation_mix") if isinstance(profile.get("recommendation_mix"), dict) else {}
    default_quotas = {"main": 0.50, "target_company": 0.25, "adjacent": 0.20, "exploration": 0.05}
    if set(configured_mix) >= set(default_quotas):
        raw_quotas = {key: float(configured_mix[key]) for key in default_quotas}
        quotas = raw_quotas if all(value >= 0 for value in raw_quotas.values()) and abs(sum(raw_quotas.values()) - 100) < 0.001 else default_quotas
        if quotas is not default_quotas:
            quotas = {key: value / 100 for key, value in quotas.items()}
    else:
        quotas = default_quotas
    selected = []
    for pool_name, ratio in quotas.items():
        count = min(len(pools[pool_name]), max(1, round(limit * ratio))) if pools[pool_name] else 0
        selected.extend(pools[pool_name][:count])
    return {
        "strategy": quotas,
        "pools": {key: values[:limit] for key, values in pools.items()},
        "items": selected[:limit],
        "total_eligible": sum(len(values) for values in pools.values()),
    }


def _qualification_dimension(job: dict, profile: dict) -> dict:
    """Expose qualification evidence without inventing a pass/fail decision."""
    education = str(profile.get("education") or "").lower()
    degree = str(job.get("degree") or "").lower()
    evidence = [f"candidate={education}; job={degree}"] if education and degree else []
    return {"status": "review" if evidence else "unconfirmed", "evidence": evidence}


def _adjacent_explanation(job: dict, profile: dict) -> str:
    adjacent = [str(value) for value in profile.get("adjacent_roles", []) if value]
    if not adjacent:
        return "岗位与当前画像存在可迁移方向，建议结合具体要求确认。"
    return f"岗位文本命中相邻方向：{', '.join(adjacent[:3])}；建议重点核对技能和工作内容。"


def _competition_risk(job: dict) -> tuple[str, list[str]]:
    """Return an estimated public-signal risk label, never an admission probability."""
    text = " ".join(str(job.get(key) or "") for key in ("title", "category", "requirements")).lower()
    basis: list[str] = []
    if any(token in text for token in ("algorithm", "ai", "machine learning", "deep learning", "算法", "人工智能")):
        basis.append("算法/AI岗位通常候选人集中")
    if any(token in text for token in ("master", "phd", "硕士", "博士")):
        basis.append("岗位要求较高学历")
    if basis:
        return "high", basis
    if any(token in text for token in ("engineer", "developer", "研发", "开发", "data", "数据")):
        return "medium", ["技术岗位公开竞争信号有限，按岗位族给出中等估计"]
    return "low", ["当前岗位文本未发现高竞争公开信号；不是录取概率"]


def query_companies(
    keyword: str = "",
    ats_type: str = "",
    official_status: str = "",
    integration_status: str = "",
    limit: int = 100,
) -> list[dict]:
    clauses = ["c.status='active'"]
    params: list[Any] = []
    if keyword:
        clauses.append("(c.canonical_name LIKE ? OR c.brand_name LIKE ?)")
        q = f"%{keyword}%"
        params.extend([q, q])
    if ats_type:
        clauses.append("EXISTS (SELECT 1 FROM career_sources s WHERE s.company_id=c.id AND s.ats_type=?)")
        params.append(ats_type)
    if official_status:
        clauses.append("EXISTS (SELECT 1 FROM career_sources s WHERE s.company_id=c.id AND s.official_status=?)")
        params.append(official_status)
    if integration_status:
        clauses.append("EXISTS (SELECT 1 FROM career_sources s WHERE s.company_id=c.id AND s.integration_status=?)")
        params.append(integration_status)
    params.append(min(max(limit, 1), 500))
    sql = f"""
        SELECT c.id, c.canonical_name, c.brand_name, c.official_website,
               c.official_domain, c.status, c.created_at, c.updated_at,
               COUNT(s.id) AS source_count,
               SUM(CASE WHEN s.official_status='confirmed' THEN 1 ELSE 0 END) AS confirmed_source_count,
               SUM(CASE WHEN s.integration_status='integrated' THEN 1 ELSE 0 END) AS integrated_source_count
        FROM companies c
        LEFT JOIN career_sources s ON s.company_id=c.id
        WHERE {' AND '.join(clauses)}
        GROUP BY c.id
        ORDER BY c.canonical_name
        LIMIT ?
    """
    with connect() as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


def query_company_job_directory(limit: int = 100) -> list[dict]:
    """Return the company registry enriched with currently active job counts."""
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT c.id, c.canonical_name, c.brand_name, c.official_website,
                   c.official_domain, c.status,
                   COUNT(DISTINCT s.id) AS source_count,
                   SUM(CASE WHEN s.official_status='confirmed' THEN 1 ELSE 0 END)
                       AS confirmed_source_count,
                   SUM(CASE WHEN s.integration_status='integrated' THEN 1 ELSE 0 END)
                       AS integrated_source_count,
                   MAX(CASE WHEN s.integration_status='integrated' THEN 1 ELSE 0 END)
                       AS has_integrated_source,
                   MAX(CASE WHEN s.access_status='reachable' THEN 1 ELSE 0 END)
                       AS has_reachable_source,
                   MAX(s.last_success_at) AS last_success_at,
                   MAX(s.paused_reason) AS paused_reason,
                   COUNT(DISTINCT CASE WHEN j.status='active' THEN j.id END)
                       AS active_job_count
            FROM companies c
            LEFT JOIN career_sources s ON s.company_id=c.id
            LEFT JOIN jobs j ON j.company=c.canonical_name
                              OR j.company=c.brand_name
                              OR j.company LIKE c.canonical_name || '%'
            WHERE c.status='active'
            GROUP BY c.id
            ORDER BY active_job_count DESC, c.canonical_name
            LIMIT ?
            """,
            (min(max(limit, 1), 500),),
        ).fetchall()
    return [dict(row) for row in rows]


def query_company_sources(
    company: str = "",
    ats_type: str = "",
    official_status: str = "",
    access_status: str = "",
    integration_status: str = "",
    quality_level: str = "",
    integration_priority: int | None = None,
    enabled: int | None = None,
    limit: int = 200,
) -> list[dict]:
    clauses = ["c.status='active'"]
    params: list[Any] = []
    if company:
        clauses.append("(c.canonical_name=? OR c.canonical_name LIKE ?)")
        params.extend([company, f"%{company}%"])
    for column, value in (
        ("s.ats_type", ats_type),
        ("s.official_status", official_status),
        ("s.access_status", access_status),
        ("s.integration_status", integration_status),
        ("s.quality_level", quality_level),
    ):
        if value:
            clauses.append(f"{column}=?")
            params.append(value)
    if integration_priority is not None:
        clauses.append("s.integration_priority=?")
        params.append(integration_priority)
    if enabled is not None:
        clauses.append("s.enabled=?")
        params.append(enabled)
    params.append(min(max(limit, 1), 500))
    sql = f"""
        SELECT s.*, c.canonical_name AS company_name
        FROM career_sources s
        JOIN companies c ON c.id=s.company_id
        WHERE {' AND '.join(clauses)}
        ORDER BY c.canonical_name, s.id
        LIMIT ?
    """
    with connect() as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


def company_source_stats() -> dict:
    with connect() as conn:
        def scalar(sql: str, params: tuple[Any, ...] = ()):
            return conn.execute(sql, params).fetchone()[0]

        def grouped(column: str):
            return [
                {"value": row[0], "count": row[1]}
                for row in conn.execute(
                    f"SELECT {column}, COUNT(*) FROM career_sources GROUP BY {column} ORDER BY {column}"
                ).fetchall()
            ]

        return {
            "companies": scalar("SELECT COUNT(*) FROM companies WHERE status='active'"),
            "sources": scalar("SELECT COUNT(*) FROM career_sources"),
            "confirmed_official_sources": scalar(
                "SELECT COUNT(*) FROM career_sources WHERE official_status='confirmed'"
            ),
            "candidate_or_unverified_sources": scalar(
                "SELECT COUNT(*) FROM career_sources WHERE official_status IN ('candidate','unverified')"
            ),
            "reachable_sources": scalar(
                "SELECT COUNT(*) FROM career_sources WHERE access_status='reachable'"
            ),
            "abnormal_or_blocked_sources": scalar(
                "SELECT COUNT(*) FROM career_sources WHERE access_status IN ('access_error','blocked')"
            ),
            "by_ats_type": grouped("ats_type"),
            "by_official_status": grouped("official_status"),
            "by_access_status": grouped("access_status"),
            "by_integration_status": grouped("integration_status"),
            "by_quality_level": grouped("quality_level"),
            "by_integration_priority": grouped("integration_priority"),
        }


def facets() -> dict:
    with connect() as conn:
        def values(column: str):
            return [
                r[0] for r in conn.execute(
                    f"SELECT DISTINCT {column} FROM jobs "
                    f"WHERE status='active' AND {column} IS NOT NULL AND TRIM({column})<>'' "
                    f"ORDER BY {column}"
                ).fetchall()
            ]

        total = conn.execute("SELECT COUNT(*) FROM jobs WHERE status='active'").fetchone()[0]
        return {
            "total": total,
            "companies": values("company"),
            "cities": values("city"),
            "categories": values("category"),
            "job_natures": values("job_nature"),
            "degrees": values("degree"),
            "job_families": values("job_family"),
        }


def job_quality_summary() -> dict:
    """Return an auditable quality report for active and quarantined rows."""
    init_db()
    required = ("company", "title", "city", "job_nature", "apply_url", "source_url")
    with connect() as conn:
        total = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        active = conn.execute("SELECT COUNT(*) FROM jobs WHERE status='active'").fetchone()[0]
        quarantined = conn.execute("SELECT COUNT(*) FROM jobs WHERE status='quarantined'").fetchone()[0]
        rejected_observations = conn.execute("SELECT COUNT(*) FROM job_quarantine").fetchone()[0]
        missing = {}
        for field in required:
            missing[field] = conn.execute(
                f"SELECT COUNT(*) FROM jobs WHERE status='active' AND (\"{field}\" IS NULL OR TRIM(\"{field}\")='')"
            ).fetchone()[0]
        missing["description_or_requirements"] = conn.execute(
            """SELECT COUNT(*) FROM jobs WHERE status='active'
               AND (COALESCE(TRIM(description),'')='' AND COALESCE(TRIM(requirements),'')='')"""
        ).fetchone()[0]
    return {
        "total": total,
        "active": active,
        "quarantined": quarantined,
        "rejected_observations": rejected_observations,
        "missing_active_fields": missing,
    }
