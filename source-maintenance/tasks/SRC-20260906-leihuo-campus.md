# SRC-20260906-leihuo-campus

- State: integrated
- Company: 网易游戏雷火
- Source ID: leihuo-campus
- Owner/agent: Codex
- Started at: 2026-09-06 (+08:00)
- Target scope: campus full-time

## Baseline

- Registry row/status: existing generated row; promoted only after direct official evidence and successful run
- Existing active jobs: 0
- Existing adapter/config: new company-specific public JSON API adapter
- Related dirty files: prior source integrations and user files preserved

## Official evidence

- Official company site: https://leihuo.163.com/campus
- Career entry/final URL: https://leihuo.163.com/campus
- Ownership evidence URL and visible evidence: the page is titled 网易游戏雷火校园招聘 and exposes the 雷火 campus job list
- ATS/platform: self-hosted public JSON API
- Public list URL: https://xiaozhao.leihuo.netease.com/api/apply/job/list/show
- Concrete detail URL: https://campus.163.com/app/detail/index?id=3738&projectId=77
- Access-control signals: public 200 responses; no login, CAPTCHA, 403, 429, proxy, or access-control bypass used

## Collection contract

- Listing endpoint/page: GET `/api/apply/job/list/show` with `project_id=77`, page 1, page size 10
- Detail endpoint/page: GET `/api/apply/job/detail/show?job_id=<ehr_job_id>&project_id=77`
- Stable source job ID: `ehr_job_id`
- Pagination/cursor and termination: API reports `pages_count=7` and `count_number=64`; this integration intentionally takes only the first page
- Source-reported total: 64
- Intentional caps: 10 records
- Snapshot complete: no
- Completeness evidence: first-page sample only; no full-snapshot claim

## Field evidence sample

| Field | Normalized value | Official evidence location |
|---|---|---|
| title | 虚拟世界架构师（游戏战斗策划） | list/detail `job_name` |
| company | 网易游戏雷火 | official campus page |
| city | 杭州 | list/detail `work_place_name` |
| job_nature | 全职 | list/detail `type_name` |
| degree | 未注明 | detail requirement has no explicit degree |
| graduate_year | 2027 | list/detail `target` |
| category/job_family | 游戏策划 / normalized taxonomy | list/detail `category_name` |
| description | official job description | detail `job_description` |
| requirements | official job requirements | detail `job_requirement` |
| apply_url | official detail route | list/detail `job_detail_url` |

## Implementation and validation

- Changed files: `config/sources.json`, `crawler/adapters/leihuo.py`, `crawler/adapters/__init__.py`, `crawler/source_registry.py`, `tests/fixtures/leihuo_position.json`, `tests/test_leihuo_adapter.py`, `tests/test_adapter_registry.py`
- Fixture/tests: added sanitized detail fixture and normalization/registry tests
- Single-source command: `CRAWL_MIN_INTERVAL_SECONDS=0 python -m crawler.worker --source leihuo-campus` (one retry after an internal stop_reason handling fix)
- jobs_found/created/updated: 10 / 10 / 0
- accepted/quarantined: 10 / 0
- Focused tests: passed
- Full tests: `python -m unittest discover -s tests -q` — 130 passed
- `validate_source.py` result: passed with `--min-jobs 3`
- UI/API verification: official list and detail APIs returned 200 with concrete job data
- Public snapshot export: generated; 3203 active jobs

## Outcome

- Final source states: confirmed / reachable / integrated
- Active jobs after run: 10
- Complete active snapshot: no
- Blocker/risks: the source has 64 reported jobs but this integration is intentionally capped at 10
- Exact next action: continue with a different unfailed source; do not retry this bounded sample until its cooldown
