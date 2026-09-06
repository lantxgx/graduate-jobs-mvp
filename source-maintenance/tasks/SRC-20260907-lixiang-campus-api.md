# SRC-20260907-lixiang-campus-api

- State: integrated
- Company: 理想汽车
- Source ID: lixiang-campus-api
- Owner/agent: Codex
- Started at: 2026-09-07 (+08:00)
- Target scope: campus full-time and campus internship

## Baseline

- Registry row/status: candidate / unknown / analyzing; 0 active jobs
- Existing active jobs: 0
- Existing adapter/config: new bounded public HTTP API adapter
- Related dirty files: preserve existing source integrations, backups, and user files

## Official evidence

- Official company site: https://www.lixiang.com/
- Career entry/final URL: https://www.lixiang.com/employ/campus.html?fromJob=1
- Ownership evidence URL and visible evidence: official 理想汽车 campus page; its public frontend calls the Li Auto recruitment API
- ATS/platform: company public JSON API (`api-web.lixiang.com`)
- Public list URL: `https://api-web.lixiang.com/osd-hr-recruitment-website/v1/recruit/school/job-page?page=1&page_size=20&project_id=4`
- Concrete detail URL: `https://www.lixiang.com/employ/detail/18946.html?fromJob=1`
- Access-control signals: public GET list/detail responses returned success without login, CAPTCHA, proxy, or access-control bypass

## Collection contract

- Listing endpoint/page: public school `job-page` API, project 4, first page capped at 20
- Detail endpoint/page: public `job/detail?job_id=<id>` API and official detail URL
- Stable source job ID: public numeric job ID
- Pagination/cursor and termination: not exhausted; API reported 21 pages and 1033 records at the first probe
- Source-reported total: 1033 in the live response
- Intentional caps: first run capped at 20; `snapshot_complete=false`
- Completeness evidence: bounded sample only; no old jobs were deactivated

## Field evidence sample

| Field | Normalized value | Official evidence location |
|---|---|---|
| title | 大模型分布式训练系统与网络互联方向实习生 | public detail response |
| company | 理想汽车 | official campus page |
| city | 上海 | detail `location_title` |
| job_nature | 实习 | detail `job_mode_name` |
| degree | 未注明 | detail did not expose a degree field for this sample |
| graduate_year | 未注明 | not explicit in detail response |
| category/job_family | 算法 | detail `second_job_function_title` |
| description | official HTML duties | detail `description` |
| requirements | official HTML requirements | detail `requirements` |
| apply_url | official 理想 detail route | same official recruitment site |

## Implementation and validation

- Changed files: `crawler/adapters/lixiang.py`, `crawler/adapters/__init__.py`, `config/sources.json`, `tests/test_lixiang_adapter.py`, fixture, registry, and this task record
- Fixture/tests: `tests/fixtures/lixiang_job.json`; focused parser test passed
- Single-source command: `python -m crawler.worker --source lixiang-campus-api`
- jobs_found/created/updated: 20 / 20 / 0
- accepted/quarantined: 20 / 0
- Focused tests: 3 passed for adapter and registry
- Full tests: `python -m unittest discover -s tests -q` — 132 passed
- `validate_source.py` result: active contract passed; registry promotion applied after evidence review
- UI/API verification: `/api/job-quality` must show no missing active required fields
- Public snapshot export: generated; 3233 active jobs and 82 companies

## Outcome

- Final source states: confirmed / reachable / integrated after promotion
- Active jobs after run: 20
- Complete active snapshot: no
- Blocker/risks: only the first 20 of 1033 reported records were collected; future refreshes must remain bounded and must not claim completeness
- Exact next action: export the accepted sample after full tests, then continue with another unfailed source
