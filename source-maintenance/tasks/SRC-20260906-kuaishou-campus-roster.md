# SRC-20260906-kuaishou-campus-roster

- State: integrated
- Company: 快手
- Source ID: kuaishou-campus-roster
- Owner/agent: Codex
- Started at: 2026-09-06 (+08:00)
- Target scope: campus full-time

## Baseline

- Registry row/status: candidate / reachable / analyzing; no previous crawl attempt with this adapter
- Existing active jobs: 0
- Existing adapter/config: previous generic `custom_html` entry; replaced only this source with a dedicated public API adapter
- Related dirty files: existing unrelated changes and database backups preserved

## Official evidence

- Official company site: https://www.kuaishou.com/
- Career entry/final URL: https://campus.kuaishou.cn/#/campus/index
- Ownership evidence URL and visible evidence: the public page is the Kuaishou campus recruitment portal and exposes the campus job navigation and job detail routes
- ATS/platform: Kuaishou self-hosted public recruitment API
- Public list URL: https://campus.kuaishou.cn/recruit/campus/e/api/v1/open/positions/simple
- Concrete detail URL: https://campus.kuaishou.cn/recruit/campus/e/api/v1/open/positions/find?id=13101&positionStatus=Release
- Access-control signals: normal public GET/POST requests returned 200; no login, CAPTCHA, 403, 429, proxy, or access-control bypass used

## Collection contract

- Listing endpoint/page: POST `/recruit/campus/e/api/v1/open/positions/simple` with project `20271779425607`, `pageNum=1`, `pageSize=20`
- Detail endpoint/page: GET `/recruit/campus/e/api/v1/open/positions/find?id=<id>&positionStatus=Release`
- Stable source job ID: numeric public position `id`
- Pagination/cursor and termination: listing response reported `total=267`; first integration deliberately collected page 1 only
- Source-reported total: 267
- Intentional caps: 20 records for the first integration
- Snapshot complete: no
- Completeness evidence: total exceeds the bounded first page; remaining records were not deactivated or claimed complete

## Field evidence sample

| Field | Normalized value | Official evidence location |
|---|---|---|
| title | public `name` | detail API result |
| company | 快手 | official campus portal |
| city | `workLocationDicts[].name` | detail API result |
| job_nature | `fulltime` → 全职 | detail API result and campus channel |
| degree | inferred only from explicit requirement text | `positionDemand` |
| graduate_year | preserved when explicit | release/project metadata |
| category/job_family | normalized from title and duties | `name`/`description` |
| description | public `description` | detail API result |
| requirements | public `positionDemand` | detail API result |
| apply_url | public hash detail route | official campus portal |

## Implementation and validation

- Changed files: `config/sources.json`, `crawler/adapters/kuaishou.py`, `crawler/adapters/__init__.py`, `crawler/source_registry.py`, `tests/fixtures/kuaishou_position.json`, `tests/test_kuaishou_adapter.py`, `tests/test_adapter_registry.py`
- Fixture/tests: added sanitized API fixture and normalization/registry tests
- Single-source command: `python -m crawler.worker --source kuaishou-campus-roster`
- jobs_found/created/updated: 267 reported / 20 accepted / 20 created / 0 updated
- accepted/quarantined: 20 / 0 for the collected page
- Focused tests: 3 passed
- Full tests: `python -m unittest discover -s tests -q` — 128 passed
- `validate_source.py` result: passed with `--min-jobs 3`
- UI/API verification: public detail API returned concrete duties, requirements, locations, and stable IDs
- Public snapshot export: generated; 3173 active jobs, including 20 快手 jobs

## Outcome

- Final source states: confirmed / reachable / integrated
- Active jobs after run: 20
- Complete active snapshot: no
- Blocker/risks: 247 public positions remain outside the intentionally bounded first page
- Exact next action: run full tests, export the 3173-job public snapshot, then probe the next source with no prior failure evidence
