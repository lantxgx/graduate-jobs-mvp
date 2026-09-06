# SRC-20260907-sohu-moka-campus

- State: blocked
- Company: 搜狐
- Source ID: sohu-moka-campus
- Owner/agent: Codex
- Started at: 2026-09-07 (+08:00)
- Target scope: campus full-time and campus internship

## Baseline

- Registry row/status: not yet synchronized; 0 active jobs
- Existing active jobs: 0
- Existing adapter/config: reusable Moka adapter with public SSR `init-data` fallback
- Related dirty files: preserve existing source integrations, backups, and user files

## Official evidence

- Official company site: https://www.sohu.com/
- Career entry/final URL: https://app.mokahr.com/campus_apply/sohu/5682#/jobs
- Ownership evidence URL and visible evidence: public portal title is “搜狐 -校园招聘” and its embedded public metadata reports 13 jobs
- ATS/platform: Moka public campus recruitment portal
- Public list URL: https://app.mokahr.com/campus_apply/sohu/5682#/jobs
- Concrete detail URL: not retained as active; detail observations did not satisfy the requirements gate
- Access-control signals: HTTP 200 public HTML with embedded job data; no login, CAPTCHA, proxy, or access-control bypass used

## Collection contract

- Listing endpoint/page: public Moka campus list; initial cap 13
- Detail endpoint/page: public Moka detail route for each listed job
- Stable source job ID: embedded public Moka UUID
- Pagination/cursor and termination: sample only; no complete traversal claim
- Source-reported total: 13; embedded list contains 13 records
- Intentional caps: first run capped at 13; `snapshot_complete=false`
- Completeness evidence: 13 records were observed, all rejected/quarantined; no complete snapshot claim

## Field evidence sample

| Field | Normalized value | Official evidence location |
|---|---|---|
| title | pending worker run | embedded Moka listing/detail |
| company | 搜狐 | portal title/metadata |
| city | pending worker run | Moka detail header |
| job_nature | pending worker run | listing/detail |
| degree | pending worker run | official requirements |
| graduate_year | pending worker run | official detail if explicit |
| category/job_family | pending worker run | title and duties |
| description | pending worker run | Moka detail body |
| requirements | pending worker run | Moka detail body |
| apply_url | pending worker run | official Moka detail route |

## Implementation and validation

- Changed files: `config/sources.json`, this task record
- Fixture/tests: reuse existing Moka SSR parser and tests
- Single-source command: `python -m crawler.worker --source sohu-moka-campus`
- jobs_found/created/updated: 13 observed / 0 / 0
- accepted/quarantined: 0 / 13 (`quality_gate_rejected`)
- Focused tests: existing Moka parser tests remain passing
- Full tests: not rerun after this source-only attempt
- `validate_source.py` result: not run; no active jobs
- UI/API verification: no active rows were created
- Public snapshot export: not run

## Outcome

- Final source states: candidate / reachable / analyzing; sample failed the independent-requirements gate
- Active jobs after run: 0
- Complete active snapshot: no
- Blocker/risks: all 13 public records lacked an independently accepted requirements field in this bounded run; raw observations remain quarantined
- Exact next action: do not retry without a new detail contract; continue with another unfailed source

## Final bounded probe (2026-09-07)

- A later worker probe did not return a public job list in the short allowed window and was stopped before another request.
- Run record was marked failed with `bounded_probe_timeout`; no jobs were written and no existing jobs were deactivated.
- Stop decision: disable this source for the fast batch and do not retry without changed evidence.
