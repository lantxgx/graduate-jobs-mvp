# SRC-20260907-bilibili-campus-roster

- State: integrated
- Company: 哔哩哔哩
- Source ID: bilibili-campus-roster
- Owner/agent: Codex
- Started at: 2026-09-07 (+08:00)
- Target scope: campus full-time

## Baseline

- Registry row/status: candidate / unknown / analyzing; 0 active jobs
- Existing active jobs: 0
- Existing adapter/config: `custom_html` placeholder; replaced with dedicated public API adapter
- Related dirty files: preserve existing user task edits, backups, and probe files

## Official evidence

- Official company site: https://www.bilibili.com/
- Career entry/final URL: https://jobs.bilibili.com/campus/positions?type=1
- Ownership evidence URL and visible evidence: official `jobs.bilibili.com` page titled 哔哩哔哩招聘 and campus navigation
- ATS/platform: self-hosted public JSON API
- Public list URL: `POST https://jobs.bilibili.com/api/campus/position/positionList`
- Concrete detail URL: https://jobs.bilibili.com/campus/positions/30368?type=3
- Access-control signals: ordinary browser page request returned 200; no login, CAPTCHA, proxy, or bypass used

## Collection contract

- Listing endpoint/page: public page obtains CSRF from `/api/auth/v1/csrf/token`, then posts campus/full-time filters to `positionList`
- Detail endpoint/page: `GET /api/campus/position/detail/{id}`
- Stable source job ID: official numeric `id`
- Pagination/cursor and termination: API reports `total=92`, `pages=10`; this first integration intentionally requests page 1 only and caps at 20 jobs
- Source-reported total: 92 at verification time
- Intentional caps: 20 jobs; sample is incomplete
- Snapshot complete: no
- Completeness evidence: list response contained concrete rows and a reported total; no full traversal claimed

## Field evidence sample

| Field | Normalized value | Official evidence location |
|---|---|---|
| title | SLG游戏版本运营【2027届】 | list/detail `positionName` |
| company | 哔哩哔哩 | official recruitment domain |
| city | 上海 | list/detail `workLocation` |
| job_nature | 全职 | list/detail `positionTypeName` |
| degree | 本科及以上 | detail `positionDescription` work requirements |
| graduate_year | 2027 | title/detail requirement text; adapter extracts explicit `20xx届`/`20xx graduate` |
| category/job_family | 运营 | `postCodeName=游戏类` plus title evidence |
| description | official work duties | detail `positionDescription` |
| requirements | official work requirements | detail `positionDescription` |
| apply_url | https://jobs.bilibili.com/campus/positions/30368?type=3 | stable official detail route |

## Implementation and validation

- Changed files: `crawler/adapters/bilibili.py`, adapter registry, `config/sources.json`, source registry allowlist, focused test and fixture
- Fixture/tests: `tests/fixtures/bilibili_position.json`, `tests/test_bilibili_adapter.py`
- Single-source command: `python -m crawler.worker --source bilibili-campus-roster`
- jobs_found/created/updated: 20 / 20 / 0
- accepted/quarantined: 20 / 0
- Focused tests: passed adapter and registry tests
- Full tests: 137 tests passed
- `validate_source.py` result: passed; registry promotion completed after source sync
- UI/API verification: local API contains 20 active 哔哩哔哩 jobs
- Public snapshot export: generated after the source run

## Outcome

- Final source states: confirmed / reachable / integrated; sampled incomplete snapshot
- Active jobs after run: 20
- Complete active snapshot: no
- Blocker/risks: source has 92 reported jobs; only the bounded first page was collected
- Exact next action: include this source in the next 10-company publication batch; do not claim full source completeness
