# SRC-20260907-leyuan-moka-campus

- State: blocked
- Company: 乐元素
- Source ID: leyuan-moka-campus
- Owner/agent: Codex
- Started at: 2026-09-07 (+08:00)
- Target scope: campus full-time and campus internship

## Baseline

- Registry row/status: not yet synchronized; 0 active jobs
- Existing active jobs: 0
- Existing adapter/config: reusable Moka adapter with public SSR `init-data` fallback
- Related dirty files: preserve existing source integrations, backups, and user files

## Official evidence

- Official company site: https://www.leyou.com/
- Career entry/final URL: https://app.mokahr.com/campus_apply/leyuansu/2357#/jobs
- Ownership evidence URL and visible evidence: public portal title is “乐元素 - 校园招聘” and its embedded public metadata reports 30 jobs
- ATS/platform: Moka public campus recruitment portal
- Public list URL: https://app.mokahr.com/campus_apply/leyuansu/2357#/jobs
- Concrete detail URL: not reached; the bounded browser run did not observe the public list
- Access-control signals: HTTP 200 public HTML with embedded job data; no login, CAPTCHA, proxy, or access-control bypass used

## Collection contract

- Listing endpoint/page: public Moka campus list; initial cap 15
- Detail endpoint/page: public Moka detail route for each listed job
- Stable source job ID: embedded public Moka UUID
- Pagination/cursor and termination: sample only; no complete traversal claim
- Source-reported total: 30; embedded first slice contains 15 records
- Intentional caps: first run capped at 15; `snapshot_complete=false`
- Completeness evidence: none; listing extraction stopped at `public_job_list_missing`

## Field evidence sample

| Field | Normalized value | Official evidence location |
|---|---|---|
| title | pending worker run | embedded Moka listing/detail |
| company | 乐元素 | portal title/metadata |
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
- Single-source command: `python -m crawler.worker --source leyuan-moka-campus`
- jobs_found/created/updated: 0 / 0 / 0
- accepted/quarantined: 0 / 0
- Focused tests: not run; no adapter change for this source
- Full tests: not run; no adapter change for this source
- `validate_source.py` result: not run; no active jobs
- UI/API verification: direct public HTML probe exposed embedded job data, but the single worker run returned `public_job_list_missing`
- Public snapshot export: not run

## Outcome

- Final source states: candidate / access unknown / analyzing; bounded attempt failed
- Active jobs after run: 0
- Complete active snapshot: no
- Blocker/risks: browser-rendered route did not expose the public list to the existing adapter; no bypass or repeated retry
- Exact next action: do not retry without new adapter evidence; continue with another unfailed source

## Final bounded probe (2026-09-07)

- A later worker probe did not return a public job list in the short allowed window and was stopped before another request.
- Run record was marked failed with `bounded_probe_timeout`; no jobs were written and no existing jobs were deactivated.
- Stop decision: disable this source for the fast batch and do not retry without changed evidence.
