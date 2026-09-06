# SRC-20260906-kingdee-moka-campus

- State: integrated
- Company: 金蝶国际
- Source ID: kingdee-moka-campus
- Owner/agent: Codex
- Started at: 2026-09-06 (+08:00)
- Target scope: campus full-time and campus internship

## Baseline

- Registry row/status: candidate / unknown / analyzing; 0 active jobs
- Existing active jobs: 0
- Existing adapter/config: reusable Moka adapter
- Related dirty files: prior source integrations and user files preserved

## Official evidence

- Official company site: https://www.kingdee.com/
- Career entry/final URL: https://campus.kingdee.com/campus-recruitment/kingdeehr/166565?locale=zh-CN
- Ownership evidence URL and visible evidence: the official Kingdee campus portal identifies 金蝶国际 and exposes the campus job list and detail routes
- ATS/platform: Moka public campus portal
- Public list URL: https://campus.kingdee.com/campus-recruitment/kingdeehr/166565?locale=zh-CN#/jobs
- Concrete detail URL: official Moka detail route under the same portal, e.g. `#/job/<public-job-id>`
- Access-control signals: public page and detail content were reachable without login, CAPTCHA, proxy, or access-control bypass

## Collection contract

- Listing endpoint/page: public Moka campus list; adapter collects a bounded first-page sample
- Detail endpoint/page: public Moka detail route for each listed job
- Stable source job ID: public Moka job identifier
- Pagination/cursor and termination: first-page bounded collection; no complete traversal claim
- Source-reported total: not used for completeness
- Intentional caps: configured sample capped at 10; 8 concrete listings returned
- Snapshot complete: no
- Completeness evidence: sample only

## Field evidence sample

| Field | Normalized value | Official evidence location |
|---|---|---|
| title | 应用开发工程师-AI（深圳） | Moka detail title |
| company | 金蝶国际 | official Moka campus portal |
| city | 深圳 | Moka detail location |
| job_nature | 全职 | Moka detail/list nature |
| degree | 本科及以上 | official requirements |
| graduate_year | 未注明 | not explicitly exposed in accepted detail |
| category/job_family | 算法/AI or software研发 | title and official duties normalized conservatively |
| description | official duties | Moka detail body |
| requirements | official requirements | Moka detail body |
| apply_url | official Moka detail route | same portal |

## Implementation and validation

- Changed files: `crawler/source_registry.py`, this task record, and generated database/public snapshot state
- Fixture/tests: reused the existing Moka adapter and its existing tests
- Single-source command: `python -m crawler.worker --source kingdee-moka-campus`
- jobs_found/created/updated: 8 / 8 / 0
- accepted/quarantined: 6 / 2; the two missing independent requirements were quarantined with raw evidence preserved
- Focused tests: existing Moka tests passed as part of the full suite
- Full tests: `python -m unittest discover -s tests -q` — 130 passed
- `validate_source.py` result: passed with `--min-jobs 3`; 6 active jobs satisfy the contract
- UI/API verification: official Moka list and detail content were returned during the worker run
- Public snapshot export: generated; 3209 active jobs

## Outcome

- Final source states: confirmed / reachable / integrated after validation
- Active jobs after run: 6
- Complete active snapshot: no
- Blocker/risks: the first sample is capped; 2 incomplete observations remain quarantined and are not shown as active jobs
- Exact next action: continue with another unfailed source; do not retry the capped sample until its cooldown
