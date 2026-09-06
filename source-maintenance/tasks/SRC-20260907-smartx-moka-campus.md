# SRC-20260907-smartx-moka-campus

- State: blocked
- Company: 北京志凌海纳科技股份有限公司（SmartX）
- Source ID: smartx-moka-campus
- Owner/agent: Codex
- Started at: 2026-09-07 (+08:00)
- Target scope: campus full-time and campus internship

## Baseline

- Registry row/status: not yet synchronized; 0 active jobs
- Existing active jobs: 0
- Existing adapter/config: reusable Moka adapter
- Related dirty files: preserve all existing source integrations, backups, and user files

## Official evidence

- Official company site: https://www.smartx.com/
- Career entry/final URL: https://app.mokahr.com/campus_apply/smartx/4183#/jobs
- Ownership evidence URL and visible evidence: the public Moka page title identifies “北京志凌海纳科技股份有限公司 - 校园招聘”; SmartX is the company recruitment brand used by the portal URL
- ATS/platform: Moka public campus portal
- Public list URL: https://app.mokahr.com/campus_apply/smartx/4183#/jobs
- Concrete detail URL: not reached; the bounded adapter run did not observe a concrete `#/job/<id>` route
- Access-control signals: initial HTML reachable without login, CAPTCHA, proxy, or access-control bypass; rendered job list/detail still requires bounded verification

## Collection contract

- Listing endpoint/page: public Moka campus list; initial sample cap 10
- Detail endpoint/page: public Moka detail route for each listed job
- Stable source job ID: public Moka job identifier in the detail hash route
- Pagination/cursor and termination: sample only; no complete traversal claim
- Source-reported total: not available because the rendered list was not observed
- Intentional caps: first run capped at 10 jobs and incomplete snapshot
- Snapshot complete: no
- Completeness evidence: none; the run stopped before listing extraction

## Field evidence sample

| Field | Normalized value | Official evidence location |
|---|---|---|
| title | pending worker run | Moka detail page |
| company | 北京志凌海纳科技股份有限公司 | official Moka portal title |
| city | pending worker run | Moka detail header |
| job_nature | pending worker run | Moka listing/detail |
| degree | pending worker run | official requirements |
| graduate_year | pending worker run | official detail if explicit |
| category/job_family | pending worker run | title and official duties |
| description | pending worker run | Moka detail body |
| requirements | pending worker run | Moka detail body |
| apply_url | pending worker run | same official Moka portal |

## Implementation and validation

- Changed files: `config/sources.json`, this task record
- Fixture/tests: reuse existing Moka adapter and tests unless the public contract differs
- Single-source command: `python -m crawler.worker --source smartx-moka-campus`
- jobs_found/created/updated: 0 / 0 / 0
- accepted/quarantined: 0 / 0
- Focused tests: not run; no adapter change
- Full tests: not run; no adapter change
- `validate_source.py` result: not run; no active jobs
- UI/API verification: public HTML was reachable, but the single-source worker observed `public_job_list_missing`
- Public snapshot export: not run

## Outcome

- Final source states: candidate / access unknown / analyzing; bounded attempt failed
- Active jobs after run: 0
- Complete active snapshot: no
- Blocker/risks: existing Moka adapter could not observe public job-card links in the rendered page; no login, CAPTCHA, proxy, or access-control bypass was attempted
- Exact next action: do not retry this source without new adapter evidence; continue with another unfailed source
