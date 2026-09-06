# SRC-20260907-ctrip-campus-api

- State: integrated
- Company: 携程集团
- Source ID: ctrip-campus-api
- Owner/agent: Codex
- Started at: 2026-09-07 (+08:00)
- Target scope: campus full-time

## Baseline

- Registry row/status: not registered; 0 active jobs
- Existing active jobs: 0
- Existing adapter/config: new bounded adapter for the official public API
- Related dirty files: preserve existing user task edits, backups, and probe files

## Official evidence

- Official company site: https://careers.ctrip.com/
- Career entry/final URL: https://careers.ctrip.com/#/campus
- Ownership evidence URL and visible evidence: official page identifies 携程集团 and exposes “校园招聘”; the campus page shows 2027届应届校招生
- ATS/platform: official self-hosted JSON API (response identifies `atsApiType=Moka`)
- Public list URL: `POST https://careers.ctrip.com/api/hrrecruit/getJobAd`
- Concrete detail URL: https://careers.ctrip.com/#/campus/job-detail/MJ036832
- Access-control signals: ordinary public page/API request returned 200; no login, CAPTCHA, proxy, or bypass used

## Collection contract

- Listing endpoint/page: public campus page loads `getJobAd` with `kind=1` and reports `total=56`
- Detail endpoint/page: each listing includes a concrete official `#/campus/job-detail/{fromId}` route and full duties/requirements in the public response
- Stable source job ID: official `fromId` such as `MJ036832`
- Pagination/cursor and termination: API returns a reported total; first integration requests page 1 only
- Source-reported total: 56 at verification time
- Intentional caps: 20 jobs; `snapshot_complete=false`
- Snapshot complete: no
- Completeness evidence: response contained 20 concrete records and total 56; no full traversal claimed

## Field evidence sample

| Field | Normalized value | Official evidence location |
|---|---|---|
| title | AI 产品经理 - 伦敦（2027届秋招） | `jobTitle` / detail route |
| company | 携程集团 | official campus page |
| city | 伦敦 | `工作地点：英国伦敦` |
| job_nature | 全职 | `kindName=应届校招生` |
| degree | 硕士及以上 | official “本、硕、博” requirement |
| graduate_year | 2027 | title and graduation requirement |
| category/job_family | 产品 | `jobFamilyGroupName=产品管理` |
| description | official duties | public `requirements` HTML section |
| requirements | official qualifications | public `requirements` HTML section |
| apply_url | https://careers.ctrip.com/#/campus/job-detail/MJ036832 | explicit official href |

## Implementation and validation

- Changed files: `crawler/adapters/ctrip.py`, adapter registry, `config/sources.json`, source registry allowlist, focused test and fixture
- Fixture/tests: `tests/fixtures/ctrip_job.json`, `tests/test_ctrip_adapter.py`
- Single-source command: `python -m crawler.worker --source ctrip-campus-api`
- jobs_found/created/updated: 20 / 20 / 0 initially, then 20 / 0 / 20 after the explicit graduate-year refresh
- accepted/quarantined: 20 / 0
- Focused tests: adapter and registry tests passed
- Full tests: 138 tests passed
- `validate_source.py` result: passed after registry promotion
- UI/API verification: local API contains 20 active 携程集团 jobs
- Public snapshot export: generated with 3351 active jobs

## Outcome

- Final source states: confirmed / reachable / integrated; sampled incomplete snapshot
- Active jobs after run: 20
- Complete active snapshot: no
- Blocker/risks: source reports 56 jobs; only the bounded first 20 were collected
- Exact next action: include this source in the next GitHub publication batch; do not claim full source completeness
