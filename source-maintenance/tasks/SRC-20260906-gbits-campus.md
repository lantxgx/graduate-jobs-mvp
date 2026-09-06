# SRC-20260906-gbits-campus

- State: integrated
- Company: 吉比特
- Source ID: gbits-campus
- Owner/agent: Codex
- Started at: 2026-09-06 (+08:00)
- Target scope: campus full-time

## Baseline

- Registry row/status: confirmed / reachable / integrated after bounded validation
- Existing active jobs: 0
- Existing adapter/config: new company-specific public API adapter
- Related dirty files: shared registry files already modified by this source; unrelated `icbc_chunk.js` and database backups preserved

## Official evidence

- Official company site: https://www.g-bits.com/
- Career entry/final URL: https://hr.g-bits.com/web/index.html#/home-web/home-index
- Ownership evidence URL and visible evidence: the official company site links to the G-Bits recruitment portal; the portal exposes campus recruitment positions without login
- ATS/platform: self-hosted public JSON API
- Public list URL: https://joinserver.g-bits.com:8666/humanResource/recruitmentExtranet/ExtrannetCampusPost/queryRecuitPost
- Concrete detail URL: official portal detail route represented by the public position record
- Access-control signals: no login, CAPTCHA, 403, 429, proxy, or access-control bypass used

## Collection contract

- Listing endpoint/page: the public campus-position API above, requested through a normal Playwright browser request context
- Detail endpoint/page: position data returned by the public listing response; official portal is retained as the source URL
- Stable source job ID: API position identifier
- Pagination/cursor and termination: public response reported 38 records; first bounded collection accepted 20 records
- Source-reported total: 38
- Intentional caps: 20 records for the first integration
- Snapshot complete: no
- Completeness evidence: the source reported more records than the intentionally collected sample; no complete-snapshot claim is made

## Field evidence sample

| Field | Normalized value | Official evidence location |
|---|---|---|
| title | official position title | API position record |
| company | 吉比特 | official portal/API |
| city | Xiamen/Shenzhen as reported | API position record |
| job_nature | 全职 | campus API scope and position record |
| degree | official value or 未注明 | API position record |
| graduate_year | official value when present | API position record |
| category/job_family | normalized from title/duties | API position record |
| description | official duties | API position record |
| requirements | official requirements | API position record |
| apply_url | official recruitment portal route | official portal/API |

## Implementation and validation

- Changed files: `config/sources.json`, `crawler/adapters/gbits.py`, `crawler/adapters/__init__.py`, `crawler/source_registry.py`, `tests/fixtures/gbits_position.json`, `tests/test_gbits_adapter.py`, `tests/test_adapter_registry.py`, `docs/jobs.json`
- Fixture/tests: added sanitized listing fixture and adapter/registry tests
- Single-source command: controlled source worker run for `gbits-campus`
- jobs_found/created/updated: 38 reported / 20 created / 0 updated
- accepted/quarantined: 20 / 18 not collected because the first run was intentionally capped
- Focused tests: passed
- Full tests: `python -m unittest discover -s tests -q` — 128 passed
- `validate_source.py` result: passed with `--min-jobs 3`
- UI/API verification: local public preview loaded 3153 jobs and displayed 吉比特 records
- Public snapshot export: regenerated after the next source; 3173 active jobs, including 20 吉比特 jobs

## Outcome

- Final source states: confirmed / reachable / integrated
- Active jobs after run: 20
- Complete active snapshot: no
- Blocker/risks: source reports 38 positions; the remaining 18 require a later bounded refresh
- Exact next action: run the full test suite, then select the next unfailed source with a reusable adapter
