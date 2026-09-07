# SRC-20260907-chinaums-beisen-campus

- State: integrated
- Company: 银联商务
- Source ID: `chinaums-beisen-campus`
- Owner/agent: Codex
- Started at: 2026-09-07
- Target scope: campus full-time | campus internship

## Baseline
- Registry row/status: new candidate; no active jobs
- Existing adapter/config: reusable `beisen` adapter
- Related dirty files: existing task notes and local runtime artifacts preserved

## Official evidence
- Official company site: `https://www.chinaums.com/`
- Career entry/final URL: `https://chinaums.zhiye.com/campus`
- Ownership evidence URL and visible evidence: the public portal loads without login and its tenant information identifies 银联商务支付股份有限公司 / 银联商务; navigation exposes 校园招聘、校招职位、实习生 and concrete detail links.
- ATS/platform: Beisen / zhiye.com
- Public list URL: `https://chinaums.zhiye.com/campus`
- Concrete detail URL: `https://chinaums.zhiye.com/intern/detail?jobAdId=304fc089-c85d-44d9-9fe1-9e418b259b52`
- Access-control signals: HTTP 200; no login, CAPTCHA, 403, 429, or security verification observed.

## Collection contract
- Listing endpoint/page: public `POST /api/Jobad/GetJobAdPageList`
- Detail endpoint/page: `/intern/detail?jobAdId=<Id>`
- Stable source job ID: Beisen `Id`
- Pagination/cursor and termination: Beisen page index; bounded by `max_pages=5`; run returned one accepted in-scope listing.
- Source-reported total: 1 for the configured campus/internship categories
- Intentional caps: `max_jobs=20`; initial bounded integration sample
- Snapshot complete: no
- Completeness evidence: this is a bounded sample/configured cap; do not deactivate missing jobs and do not claim full source coverage.

## Field evidence sample
| Field | Normalized value | Official evidence location |
|---|---|---|
| title | 绩效考核岗实习生(J11308) | public detail page |
| company | 银联商务 | portal tenant information |
| city | 上海市·浦东新区 | public listing/detail |
| job_nature | 实习 | internship route/category |
| degree | 未注明 | official detail omits degree |
| graduate_year | 未注明 | official detail omits cohort |
| category/job_family | normalized from official title/content | public detail |
| description | present | public detail |
| requirements | present | public detail |
| apply_url | concrete absolute official detail URL | public detail route |

## Implementation and validation
- Changed files: `config/sources.json`; `crawler/source_registry.py`; this task file
- Fixture/tests: no parser change; reused existing Beisen adapter
- Single-source command: `python -m crawler.worker --source chinaums-beisen-campus`
- jobs_found/created/updated: 1 / 1 / 0
- accepted/quarantined: 1 / 0
- Focused tests: source validation passed
- Full tests: not run yet
- `validate_source.py` result: passed; 1 active job
- UI/API verification: `/api/jobs` and local UI show data; baseline remains 152 companies before this source and now 153 with an active job
- Public snapshot export: not run

## Outcome
- Final source states: confirmed / reachable / integrated
- Active jobs after run: 1
- Complete active snapshot: no
- Blocker/risks: only one job was found in the bounded run; source remains intentionally incomplete.
- Exact next action: continue with another low-effort public source; skip and record any source that hits access controls or lacks concrete details.
