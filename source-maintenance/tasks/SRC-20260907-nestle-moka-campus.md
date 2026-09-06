# SRC-20260907-nestle-moka-campus

- State: blocked
- Company: 雀巢（Nestlé GCR）
- Source ID: nestle-moka-campus
- Owner/agent: Codex
- Started at: 2026-09-07 (+08:00)
- Target scope: campus full-time and campus internship

## Baseline

- Registry row/status: not yet synchronized; 0 active jobs
- Existing active jobs: 0
- Existing adapter/config: reusable Moka adapter with public SSR `init-data` fallback
- Related dirty files: preserve existing source integrations, backups, and user files

## Official evidence

- Official company site: https://www.nestle.com.cn/
- Career entry/final URL: https://app.mokahr.com/campus-recruitment/nestlezgc/91899#/jobs
- Ownership evidence URL and visible evidence: the public portal identifies `Nestle GCR`, its footer identifies `Nestlé雀巢`, and metadata describes the 2026 Nestle GCR campus recruitment
- ATS/platform: Moka public campus recruitment portal
- Public list URL: https://app.mokahr.com/campus-recruitment/nestlezgc/91899#/jobs
- Concrete detail URL: `https://app.mokahr.com/campus-recruitment/nestlezgc/91899#/job/c05680ad-98af-4dff-be38-12c7ce641b6a`
- Access-control signals: HTTP 200 public HTML with embedded job data; no login, CAPTCHA, proxy, or access-control bypass used

## Collection contract

- Listing endpoint/page: public Moka campus list; initial cap 15
- Detail endpoint/page: public Moka detail route for each listed job
- Stable source job ID: embedded public Moka UUID
- Pagination/cursor and termination: sample only; no complete traversal claim
- Source-reported total: 69 in public page metadata; current embedded list exposed 15 records
- Intentional caps: first run capped at 15; `snapshot_complete=false`
- Snapshot complete: no
- Completeness evidence: bounded sample only; the reported total exceeds the first-run cap

## Field evidence sample

| Field | Normalized value | Official evidence location |
|---|---|---|
| title | pending worker run | embedded Moka listing/detail |
| company | 雀巢（Nestlé GCR） | portal organization/footer metadata |
| city | pending worker run | Moka detail header |
| job_nature | pending worker run | listing/detail if exposed |
| degree | pending worker run | official requirements/detail |
| graduate_year | pending worker run | official detail if explicit |
| category/job_family | pending worker run | title and official duties |
| description | pending worker run | Moka detail body |
| requirements | pending worker run | Moka detail body |
| apply_url | pending worker run | official Moka detail route |

## Implementation and validation

- Changed files: `config/sources.json`, this task record
- Fixture/tests: reuse `parse_embedded_job_cards` coverage and existing Moka tests
- Single-source command: `python -m crawler.worker --source nestle-moka-campus`
- jobs_found/created/updated: 15 / 15 / 0 on the initial worker run; 14 were subsequently isolated by the independent-requirements gate
- accepted/quarantined: 1 active / 14 quarantined for `missing_independent_requirements`
- Focused tests: `python -m unittest tests.test_moka_jobs -v` — 6 passed
- Full tests: `python -m unittest discover -s tests -q` — 131 passed
- `validate_source.py` result: minimum-job gate not met after quality isolation (1 active job); remaining active row satisfies the active-job contract
- UI/API verification: `/api/job-quality` reports 3213 active jobs, 0 missing active required fields
- Public snapshot export: generated; 3213 active jobs and 81 companies

## Outcome

- Final source states: candidate / reachable / analyzing; one qualified job retained, source not promoted because the sample did not meet the minimum three-job validation gate
- Active jobs after run: 1
- Complete active snapshot: no
- Blocker/risks: 14 of the first 15 public records did not expose independent requirements in their detail content; they remain quarantined with raw evidence. The 69-job reported total was not traversed completely.
- Exact next action: do not claim full integration or completeness; only revisit when a new public detail contract or a different page slice provides independent requirements
