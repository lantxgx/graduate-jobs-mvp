# Low-level AI playbook: official recruitment -> SQLite -> frontend

Use this document as the repeatable operating procedure for adding one company.
The unit of work is one official source, never a large unverified URL batch.

## 0. Baseline and safety

Run from `V0.1/graduate-jobs-mvp` with the repository interpreter:

```powershell
& .\.venv\Scripts\python.exe C:\Users\lantx\.codex\skills\maintain-campus-job-data\scripts\audit_coverage.py --project-root . --target-companies 300
git status --short
```

Only use public pages controlled by the company. Stop on login, CAPTCHA, 403/429,
security verification, signed/private API, or unclear ownership. Never invent a
title, city, degree, major, duties, year, ID, or apply URL.

## 1. Verify the source before coding

Record a task file at `source-maintenance/tasks/SRC-YYYYMMDD-<source-id>.md`.
Prove all four items:

1. company-owned recruitment domain or official company link;
2. campus/graduate scope;
3. concrete public job cards;
4. concrete duties/requirements and an official application entry.

If any item is missing, record `blocked` or `analyzing` and do not insert jobs.

## 2. Discover the public contract

Prefer an existing adapter. Otherwise inspect normal page loading and classify:

- public JSON endpoint with stable ID and pagination;
- reusable ATS adapter (Feishu, Beisen, Moka, Greenhouse, Lever);
- visible HTML cards with explicit links;
- company-specific adapter as the last choice.

Create a sanitized fixture and focused parser test before a large run. Start with
3-20 jobs. Keep `snapshot_complete=false` until pagination termination is proven.

## 3. Normalize into the database contract

Every accepted row needs:

```text
source_id, source_job_id, company, title, city,
job_nature (only 全职 or 实习), category, degree,
description, requirements, apply_url, source_url, content_hash
```

Locations are split into normalized relations (`job_locations`) and majors into
(`job_majors`). Use only majors stated in official requirements; do not infer a
student major from a job title. Keep the original response in `raw` evidence.

Run one source only:

```powershell
$env:CRAWL_MIN_INTERVAL_SECONDS='0'
& .\.venv\Scripts\python.exe -m crawler.worker --source <source-id>
```

The runner quarantines rows that fail the field-quality gate. An incomplete run
must never deactivate old jobs.

## 4. Validate and publish the local frontend snapshot

```powershell
& .\.venv\Scripts\python.exe C:\Users\lantx\.codex\skills\maintain-campus-job-data\scripts\validate_source.py --project-root . --source-id <source-id> --min-jobs 3
& .\.venv\Scripts\python.exe scripts/export_standard_jobs.py --limit 300 --output data/standardized/companies-all.json
& .\.venv\Scripts\python.exe scripts/validate_standardized_jobs.py data/standardized/companies-all.json
& .\.venv\Scripts\python.exe scripts/export_github_pages.py
& .\.venv\Scripts\python.exe -m unittest discover -s tests -q
node --check static/app.js
```

The frontend reads the SQLite-backed API. Confirm `/health`, `/api/jobs`,
`/api/facets`, and one company/location/major filter in the browser. Restart the
local server only after code/config changes:

```powershell
.\restart_server.ps1
```

## 5. Completion rules

Report separately: verified companies, integrated companies, complete snapshots,
active jobs, accepted rows, quarantined rows, and blocked sources. A 20-job sample
is integrated but incomplete. Only mark complete when every in-scope public listing
is traversed and `unique listings = accepted + quarantined` is reconciled.

## Current worked examples

- Lenovo: 85 graduate positions, public paginated API, complete snapshot.
- Meituan: 20 concrete campus positions from the public page, intentionally sampled
  and incomplete because the public payload did not expose a per-job apply URL or a
  proven cursor contract.
- Bilibili, Alibaba, Baidu, Nio and Perfect World remain blocked/analyzing where
  public details or stable access could not be proven. Do not retry aggressively.
