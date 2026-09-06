# SRC-20260906-wind-campus

- State: integrated
- Company: 万得资讯
- Source ID: source-de915a7057089add
- Owner/agent: Codex
- Started at: 2026-09-06 (+08:00)
- Target scope: campus full-time and campus internship

## Baseline

- Registry row/status: candidate / reachable / analyzing; no previous crawl attempt
- Existing active jobs: 0
- Existing adapter/config: new static JavaScript payload adapter
- Related dirty files: existing unrelated changes and database backups preserved

## Official evidence

- Official company site: https://www.wind.com.cn/
- Career entry/final URL: https://www.wind.com.cn/portal/zh/JoinUs/recruit.html
- Ownership evidence URL and visible evidence: the company-owned recruitment page explicitly separates 社会招聘 and 校园招聘 and loads the campus list from its own public JS asset
- ATS/platform: self-hosted static recruitment page with public JavaScript payload
- Public list URL: https://www.wind.com.cn/portal/zh/JoinUs/js/channelPositions.js?v=20251210
- Concrete detail URL: https://www.wind.com.cn/portal/zh/JoinUs/recruit.html?positionType=9002&channelPositionId=1404
- Access-control signals: public 200 response; no login, CAPTCHA, 403, 429, proxy, or access-control bypass used

## Collection contract

- Listing endpoint/page: `channelPositions.js`, parsed from the official page's ordinary script load
- Detail endpoint/page: same official page with `positionType=9002&channelPositionId=<ChannelPositionID>`; the payload contains the detail text shown by that page
- Stable source job ID: `ChannelPositionID`
- Pagination/cursor and termination: the public payload is a bounded static list; the first integration selected active, non-expired campus rows
- Source-reported total: not separately reported; 20 accepted from the bounded first integration
- Intentional caps: 20 records
- Snapshot complete: no
- Completeness evidence: initial run is capped and does not claim to exhaust the static payload

## Field evidence sample

| Field | Normalized value | Official evidence location |
|---|---|---|
| title | `ChannelPositionName` | public JS/detail page |
| company | 万得资讯 | official recruitment page |
| city | `WorkPlace[].Name` | public JS/detail page |
| job_nature | title with 实习 → 实习, otherwise campus → 全职 | public position record |
| degree | explicit `Degree` or requirement text | public JS/detail page |
| category/job_family | `PositionClassName` normalized | public JS/detail page |
| description | `ChannelPositionDesc` | public JS/detail page |
| requirements | `ChannelPositionRequirement` | public JS/detail page |
| apply_url | official detail route | official recruitment page |

## Implementation and validation

- Changed files: `config/sources.json`, `crawler/adapters/wind.py`, `crawler/adapters/__init__.py`, `crawler/source_registry.py`, `tests/fixtures/wind_position.json`, `tests/test_wind_adapter.py`, `tests/test_adapter_registry.py`
- Fixture/tests: added sanitized payload fixture and normalization/registry tests
- Single-source command: `python -m crawler.worker --source source-de915a7057089add`
- jobs_found/created/updated: 20 / 20 / 0
- accepted/quarantined: 20 / 0 for the bounded active campus selection
- Focused tests: passed
- Full tests: `python -m unittest discover -s tests -q` — 129 passed
- `validate_source.py` result: passed with `--min-jobs 3`
- UI/API verification: public JavaScript payload and concrete detail route verified
- Public snapshot export: generated; 3193 active jobs, including 20 万得资讯 jobs

## Outcome

- Final source states: confirmed / reachable / integrated
- Active jobs after run: 20
- Complete active snapshot: no
- Blocker/risks: the public page is a bounded static payload and no complete-snapshot claim is made
- Exact next action: validate, promote, run full tests, and export the public snapshot
