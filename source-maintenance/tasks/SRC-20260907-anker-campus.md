# SRC-20260907-anker-campus

- company: 安克创新（Anker Innovations）
- source_id: anker-campus-api
- official listing URL: https://career.anker-in.com/universities/recruitment/
- ATS/API: Anker official site backed by public Lark Hire API
- operator: Codex
- status: integrated bounded sample
- checked_at: 2026-09-07T00:00:00+08:00 (+08:00)

## Official public evidence

- The Anker Innovations recruitment site links the campus recruitment page and exposes campus, experienced, and internship recruitment channels.
- The campus page is publicly reachable and visibly publishes “Anker Innovations 2027 Global Campus Recruitment”.
- Normal page loading exposes a public list endpoint and a public detail endpoint; no login, CAPTCHA, security verification, proxy, or access-control bypass was used.
- List endpoint: `POST https://rainbowbridge.anker.com/api/lark/hire/v1/websites/7268177039772633400/job_posts/search?page_size=10&page_token=`.
- Detail endpoint: `GET https://rainbowbridge.anker.com/api/lark/hire/v1/websites/7268177039772633400/job_posts/{id}`. The list `id` is required; `job_id` is not accepted by the detail API.

## Scope and limits

- First integration is bounded to 10 public campus/graduate records. `snapshot_complete=false` is intentional because the API reports more pages and this run does not exhaust the cursor.
- Only records whose official `subject.name` identifies campus/graduate/internship recruitment are retained.
- Records without an official title, city, description, or requirement are rejected/quarantined by normalization and are never completed with guessed content.
- The Feishu application portal is used as the official application URL because the public Anker API does not provide a per-job apply URL: https://anker-in.jobs.feishu.cn/189381/position/application.

## Result

- list sample limit: 10
- expected active jobs after worker: 10 or fewer, depending on detail quality gates
- completeness: bounded/incomplete; do not deactivate previous jobs from this source

## Commands

```powershell
.\.venv\Scripts\python.exe -m crawler.source_registry
.\.venv\Scripts\python.exe -m crawler.worker --source anker-campus-api
python C:\Users\lantx\.codex\skills\maintain-campus-job-data\scripts\validate_source.py --project-root . --source-id anker-campus-api --min-jobs 3
```

