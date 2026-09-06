# SRC-20260907-zkxx-moka-internship

- State: implementing
- Company: 浙江中控信息产业股份有限公司（中控信息）
- Source ID: zkxx-moka-internship
- Owner/agent: Codex
- Started at: 2026-09-07 (+08:00)
- Target scope: campus internship

## Baseline

- Registry row/status: not yet synchronized; 0 active jobs
- Existing active jobs: 0
- Existing adapter/config: reusable Moka adapter
- Related dirty files: preserve all existing source integrations, backups, and user files

## Official evidence

- Official company site: https://www.supcon.com/
- Career entry/final URL: https://app.mokahr.com/campus-recruitment/zkxx/72098#/jobs
- Ownership evidence URL and visible evidence: the public Moka page title identifies “中控信息 - 实习生招聘”; page metadata identifies 浙江中控信息产业股份有限公司 and the public page embeds a jobStats total of 9
- ATS/platform: Moka public campus recruitment portal
- Public list URL: https://app.mokahr.com/campus-recruitment/zkxx/72098#/jobs
- Concrete detail URL: `https://app.mokahr.com/campus-recruitment/zkxx/72098#/job/7dbdd4c3-e908-4d6f-8703-a0bace0611c8`
- Access-control signals: public HTML returned HTTP 200 with embedded job metadata; no login, CAPTCHA, proxy, or access-control bypass used

## Collection contract

- Listing endpoint/page: public Moka internship list; initial cap 9 based on the page's embedded total
- Detail endpoint/page: public Moka detail route for each listed job
- Stable source job ID: embedded public Moka UUID
- Pagination/cursor and termination: sample bounded to the reported 9; no complete traversal claim
- Source-reported total: 9 in public page metadata
- Intentional caps: first run capped at 9; snapshot remains incomplete
- Snapshot complete: no
- Completeness evidence: public HTML exposes `jobStats.total=9`; first worker run reached the list but existing rendered-card parser produced no qualified jobs

## Field evidence sample

| Field | Normalized value | Official evidence location |
|---|---|---|
| title | pending worker run | embedded Moka listing/detail |
| company | 浙江中控信息产业股份有限公司 | page title and metadata |
| city | pending worker run | public location object/detail |
| job_nature | 实习 | embedded `commitment` fields |
| degree | pending worker run | embedded `education` fields |
| graduate_year | pending worker run | official detail if explicit |
| category/job_family | pending worker run | public title/department evidence |
| description | pending worker run | Moka detail body |
| requirements | pending worker run | Moka detail body |
| apply_url | pending worker run | official Moka detail route |

## Implementation and validation

- Changed files: `config/sources.json`, `crawler/adapters/moka.py`, `tests/test_moka_jobs.py`, this task record
- Fixture/tests: focused unit test covers public SSR `init-data` job-card parsing; no live fixture committed because the response contains current source data
- Single-source command: `python -m crawler.worker --source zkxx-moka-internship`
- jobs_found/created/updated: 0 / 0 / 0 on the initial run
- accepted/quarantined: 0 / 0 on the initial run
- Focused tests: `python -m unittest tests.test_moka_jobs -v` — 6 passed
- Full tests: pending
- `validate_source.py` result: pending; source has no active jobs
- UI/API verification: public detail route rendered concrete duties and requirements; worker rerun is waiting for the source cooldown after the initial failed run
- Public snapshot export: not run

## Outcome

- Final source states: candidate / reachable / analyzing; adapter repair applied, source rerun pending cooldown
- Active jobs after run: 0
- Complete active snapshot: no
- Blocker/risks: the worker's retry is protected by the normal source cooldown; no cooldown bypass was used
- Exact next action: rerun this source after cooldown, then validate accepted/quarantined rows and export only if gates pass
