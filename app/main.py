from __future__ import annotations

import asyncio
import json
import os
import hashlib
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, Query, HTTPException, Body
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.db import (
    init_db,
    query_jobs,
    count_jobs,
    query_jobs_with_profile,
    recommend_jobs,
    facets,
    coverage_summary,
    connect,
    query_companies,
    query_company_job_directory,
    query_company_sources,
    company_source_stats,
    query_source_snapshots,
    query_job_updates,
    get_user_profile,
    save_user_profile,
    delete_user_profile,
    set_job_action,
    query_job_actions,
    query_ingestion_queue,
    query_job_quarantine,
    job_quality_summary,
    acquire_crawl_lock,
    release_crawl_lock,
    crawl_cooldown_remaining,
    upsert_job,
)
from crawler.runner import load_sources, crawl_source, is_qualified_job
from crawler.normalize import normalize_category, normalize_degree, normalize_job_nature, normalize_city
from app.resume_parser import parse_resume_base64
from app.ai_profile import analyze_resume_text

app = FastAPI(title="牛投马面", version="0.2.0")
STATIC_DIR = Path("static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/profile")
def profile_page():
    return FileResponse(STATIC_DIR / "profile.html")


@app.get("/admin/sources")
def admin_sources_page():
    return FileResponse(STATIC_DIR / "admin-sources.html")


@app.get("/admin/manual")
def admin_manual_page():
    return FileResponse(STATIC_DIR / "admin-manual.html")


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/api/jobs")
def jobs(
    keyword: str = "",
    company: str = "",
    country: str = "",
    province: str = "",
    city: str = "",
    category: str = "",
    major: str = "",
    job_nature: str = "",
    degree: str = "",
    job_family: str = "",
    limit: int = Query(100, ge=1, le=500),
    offset: int | None = Query(None, ge=0),
):
    rows = query_jobs(
        keyword, company, city, category, job_nature, degree, limit,
        job_family, offset or 0, country, province, major,
    )
    if offset is None:
        return rows
    return {
        "items": rows,
        "total": count_jobs(
            keyword, company, city, category, job_nature, degree,
            job_family, country, province, major,
        ),
        "offset": offset,
        "limit": min(max(limit, 1), 500),
    }


@app.get("/api/facets")
def get_facets():
    return facets()


@app.get("/api/coverage-summary")
def get_coverage_summary():
    return coverage_summary()


@app.get("/api/job-quality")
def job_quality():
    return job_quality_summary()


@app.get("/api/job-quarantine")
def job_quarantine(source_id: str = "", limit: int = Query(100, ge=1, le=500)):
    return query_job_quarantine(source_id, limit)


@app.get("/api/jobs/with-profile")
def jobs_with_profile(
    keyword: str = "",
    company: str = "",
    city: str = "",
    category: str = "",
    job_nature: str = "",
    degree: str = "",
    limit: int = Query(100, ge=1, le=500),
):
    return query_jobs_with_profile(
        get_user_profile(), keyword, company, city, category, job_nature, degree, limit
    )


@app.get("/api/sources")
def sources():
    return load_sources()


@app.post("/api/manual/jobs")
def manual_jobs(payload: dict = Body(...)):
    """Insert reviewed jobs with the same canonical fields and quality gate as crawlers."""
    records = payload.get("jobs") if isinstance(payload, dict) else None
    if not isinstance(records, list) or not records:
        raise HTTPException(400, "jobs must be a non-empty list")
    required = ("company", "title", "city", "job_nature", "category", "degree", "requirements", "description", "apply_url", "source_url")
    errors, accepted = [], 0
    for index, raw in enumerate(records):
        if not isinstance(raw, dict):
            errors.append({"index": index, "error": "job_must_be_object"}); continue
        missing = [key for key in required if not str(raw.get(key) or "").strip()]
        if missing:
            errors.append({"index": index, "error": "missing_required_fields", "fields": missing}); continue
        source_url, apply_url = str(raw["source_url"]).strip(), str(raw["apply_url"]).strip()
        if not source_url.startswith(("https://", "http://")) or not apply_url.startswith(("https://", "http://")):
            errors.append({"index": index, "error": "official_http_url_required"}); continue
        company, title = str(raw["company"]).strip(), str(raw["title"]).strip()
        source_id = str(raw.get("source_id") or "manual-" + hashlib.sha1(source_url.encode()).hexdigest()[:16])
        with connect() as conn:
            row = conn.execute("SELECT id FROM companies WHERE canonical_name=?", (company,)).fetchone()
            company_id = row[0] if row else conn.execute("INSERT INTO companies(canonical_name,brand_name) VALUES (?,?)", (company, company)).lastrowid
            conn.execute("INSERT OR IGNORE INTO company_aliases(company_id,alias) VALUES (?,?)", (company_id, company))
            conn.execute("""INSERT OR IGNORE INTO career_sources(source_key,company_id,source_name,url,final_url,domain,recruitment_scope,ats_type,official_status,access_status,integration_status,discovery_source,adapter,adapter_config_json,enabled,quality_level,integration_priority)
                VALUES (?,?,?,?,?,'manual','campus','manual','candidate','reachable','integrated','manual-entry','manual','{}',1,'medium',3)""", (source_id, company_id, company + '手动录入', source_url, source_url))
        job = dict(raw)
        job.update({"source_id": source_id, "company": company, "title": title, "city": normalize_city(raw["city"]), "job_nature": normalize_job_nature(raw["job_nature"], title, raw["description"] + raw["requirements"]), "category": normalize_category(raw["category"], title, raw["description"]), "degree": normalize_degree(raw["degree"], raw["requirements"]), "source_job_id": str(raw.get("source_job_id") or hashlib.sha1((source_id + '|' + title + '|' + apply_url).encode()).hexdigest()[:24]), "raw": raw})
        job["content_hash"] = hashlib.sha256((source_id + '|' + job["source_job_id"] + '|' + title).encode()).hexdigest()
        if not is_qualified_job(job):
            errors.append({"index": index, "error": "quality_gate_rejected"}); continue
        try:
            upsert_job(job); accepted += 1
        except (ValueError, KeyError) as exc:
            errors.append({"index": index, "error": str(exc)})
    if errors and not accepted:
        raise HTTPException(422, {"accepted": 0, "errors": errors})
    return {"accepted": accepted, "rejected": len(errors), "errors": errors}


@app.get("/api/recommendations")
def recommendations(limit: int = Query(100, ge=1, le=500)):
    profile = get_user_profile()
    result = recommend_jobs(profile, limit)
    # Recommendation is an optional layer over complete search.  Do not make
    # an unconfigured user's single exploratory result look like a validated
    # personal recommendation; the UI can guide the user to /profile instead.
    result["profile_ready"] = bool(profile)
    result["needs_profile"] = not bool(profile)
    return result


@app.get("/api/job-actions")
def job_actions(action: str = ""):
    if action and action not in {"favorite", "ignore", "applied"}:
        raise HTTPException(400, "Unsupported job action")
    return query_job_actions(action)


@app.get("/api/ingestion-queue")
def ingestion_queue(limit: int = Query(100, ge=1, le=500)):
    return query_ingestion_queue(limit)


@app.post("/api/jobs/{job_id}/action")
def job_action(job_id: int, payload: dict = Body(...)):
    action = str(payload.get("action", ""))
    enabled = bool(payload.get("enabled", True))
    try:
        set_job_action(job_id, action, enabled)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {"job_id": job_id, "action": action, "enabled": enabled}


@app.get("/api/companies")
def companies(
    keyword: str = "",
    ats_type: str = "",
    official_status: str = "",
    integration_status: str = "",
    limit: int = Query(100, ge=1, le=500),
):
    return query_companies(keyword, ats_type, official_status, integration_status, limit)


@app.get("/api/company-job-directory")
def company_job_directory(limit: int = Query(100, ge=1, le=500)):
    return query_company_job_directory(limit)


@app.get("/api/companies/{company_id}/jobs")
def company_jobs(
    company_id: int,
    city: str = "",
    category: str = "",
    job_nature: str = "",
    degree: str = "",
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    with connect() as conn:
        company = conn.execute(
            "SELECT canonical_name FROM companies WHERE id=? AND status='active'",
            (company_id,),
        ).fetchone()
    if not company:
        raise HTTPException(404, "Unknown company")
    rows = query_jobs("", company[0], city, category, job_nature, degree, limit, "", offset)
    return {
        "items": rows,
        "total": count_jobs("", company[0], city, category, job_nature, degree, ""),
        "company": company[0],
        "offset": offset,
        "limit": limit,
    }


@app.get("/api/companies/{company_id}/collection-status")
def company_collection_status(company_id: int):
    with connect() as conn:
        company = conn.execute(
            "SELECT id, canonical_name FROM companies WHERE id=? AND status='active'",
            (company_id,),
        ).fetchone()
        if not company:
            raise HTTPException(404, "Unknown company")
        row = conn.execute(
            """SELECT COUNT(DISTINCT s.id) AS source_count,
                      SUM(CASE WHEN s.integration_status='integrated' THEN 1 ELSE 0 END) AS integrated_source_count,
                      MAX(s.last_success_at) AS last_success_at,
                      MIN(s.next_run_at) AS next_run_at,
                      MAX(s.paused_reason) AS paused_reason,
                      MAX(s.consecutive_failures) AS consecutive_failures
               FROM career_sources s WHERE s.company_id=?""",
            (company_id,),
        ).fetchone()
        active_jobs = conn.execute(
            "SELECT COUNT(*) FROM jobs WHERE company_id=? AND status='active'",
            (company_id,),
        ).fetchone()[0]
    return {
        "company_id": company[0],
        "company": company[1],
        "active_job_count": active_jobs,
        **dict(row),
    }


@app.get("/api/company-sources")
def company_sources(
    company: str = "",
    ats_type: str = "",
    official_status: str = "",
    access_status: str = "",
    integration_status: str = "",
    quality_level: str = "",
    integration_priority: int | None = Query(None, ge=0, le=4),
    enabled: int | None = Query(None, ge=0, le=1),
    limit: int = Query(200, ge=1, le=500),
):
    return query_company_sources(
        company, ats_type, official_status, access_status, integration_status,
        quality_level, integration_priority, enabled, limit
    )


@app.get("/api/company-source-stats")
def company_source_statistics():
    return company_source_stats()


@app.get("/api/crawl-runs")
def crawl_runs(limit: int = Query(20, ge=1, le=100)):
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT id, source_id, started_at, finished_at, status,
                   jobs_found, jobs_created, jobs_updated, error_message
            FROM crawl_runs
            ORDER BY id DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


@app.get("/api/source-snapshots")
def source_snapshots(source_id: str = "", limit: int = Query(50, ge=1, le=200)):
    return query_source_snapshots(source_id, limit)


@app.get("/api/job-updates")
def job_updates(since: str = "", limit: int = Query(100, ge=1, le=500)):
    return query_job_updates(since, limit)


@app.get("/api/profile")
def profile():
    return get_user_profile() or {"saved": False}


@app.post("/api/resume/preview")
def resume_preview(payload: dict = Body(...)):
    filename = str(payload.get("filename", ""))
    encoded = str(payload.get("content_base64", ""))
    try:
        result = parse_resume_base64(filename, encoded)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    # Result is intentionally returned only to the current request.
    return {"saved": False, **result}


@app.post("/api/resume/analyze")
def resume_analyze(payload: dict = Body(...)):
    filename = str(payload.get("filename", ""))
    encoded = str(payload.get("content_base64", ""))
    external_consent = bool(payload.get("external_ai_consent", False))
    try:
        preview = parse_resume_base64(filename, encoded)
        profile = analyze_resume_text(preview["text_preview"], external_consent)
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc
    return {"saved": False, "filename": filename, "profile": profile}


@app.put("/api/profile")
def update_profile(payload: dict = Body(...)):
    save_profile = bool(payload.pop("save_profile", True))
    # The MVP accepts only structured fields. Raw resume content is never persisted.
    payload.pop("raw_resume", None)
    payload.pop("resume_text", None)
    if not save_profile:
        return {"saved": False, "profile": payload}
    return {"saved": True, "profile": save_user_profile(payload)}


@app.delete("/api/profile")
def remove_profile():
    return {"deleted": delete_user_profile()}


async def _run_crawl_guarded(source: dict):
    import uuid
    owner = f"api-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    if not acquire_crawl_lock(source["id"], owner):
        return
    try:
        await crawl_source(source)
    finally:
        release_crawl_lock(source["id"], owner)


@app.post("/api/crawl/{source_id}")
async def crawl(source_id: str, background_tasks: BackgroundTasks):
    source = next((s for s in load_sources() if s["id"] == source_id), None)
    if not source:
        raise HTTPException(404, "Unknown source")
    remaining = crawl_cooldown_remaining(source_id, int(os.getenv("CRAWL_MIN_INTERVAL_SECONDS", "3600")))
    if remaining:
        return {"accepted": False, "source_id": source_id, "error": "crawl_cooldown_active", "cooldown_remaining_seconds": remaining}
    background_tasks.add_task(_run_crawl_guarded, source)
    return {"accepted": True, "source_id": source_id, "message": "crawl_queued"}
