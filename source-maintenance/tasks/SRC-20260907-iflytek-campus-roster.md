# SRC-20260907-iflytek-campus-roster

- State: blocked
- Company: 科大讯飞
- Source ID: iflytek-campus-roster
- Owner/agent: Codex
- Started at: 2026-09-07 (+08:00)
- Target scope: campus full-time and campus internship

## Baseline

- Registry row/status: candidate / unknown / analyzing; 0 active jobs
- Existing active jobs: 0
- Existing adapter/config: reusable visible-HTML adapter (`custom_html`); public HTML responded 200
- Related dirty files: preserve all existing source integrations and user files

## Official evidence

- Official company site: https://www.iflytek.com/
- Career entry/final URL: https://campus.iflytek.com/official-pc/jobList
- Ownership evidence URL and visible evidence: public page title is “官网 | 科大讯飞招聘” and the page is the company campus job-list domain
- ATS/platform: self-hosted public HTML/SPA entry; no login or CAPTCHA observed in the initial HTML probe
- Public list URL: https://campus.iflytek.com/official-pc/jobList
- Concrete detail URL: not reached; no concrete visible cards were exposed
- Access-control signals: initial public HTML returned HTTP 200; no bypass used

## Collection contract

- Listing endpoint/page: public job-list page; initial sample cap from existing config is 20
- Detail endpoint/page: explicit detail links exposed by visible job cards
- Stable source job ID: card ID or concrete detail URL, subject to parser evidence
- Pagination/cursor and termination: sample only; no complete traversal claim
- Source-reported total: not available
- Intentional caps: first run capped at 20 and incomplete snapshot
- Snapshot complete: no
- Completeness evidence: none; listing extraction stopped at the parser gate

## Field evidence sample

| Field | Normalized value | Official evidence location |
|---|---|---|
| title | pending worker run | visible job card/detail |
| company | 科大讯飞 | official recruitment page |
| city | pending worker run | visible card/detail |
| job_nature | pending worker run | visible card/detail |
| degree | pending worker run | official detail if exposed |
| graduate_year | pending worker run | official detail if explicit |
| category/job_family | pending worker run | visible department/title evidence |
| description | pending worker run | visible card/detail |
| requirements | pending worker run | official detail if exposed |
| apply_url | pending worker run | explicit official detail link |

## Implementation and validation

- Changed files: this task record only; the config row already existed
- Fixture/tests: reuse existing `custom_html` adapter; no parser change before evidence
- Single-source command: `python -m crawler.worker --source iflytek-campus-roster`
- jobs_found/created/updated: 0 / 0 / 0
- accepted/quarantined: 0 / 0
- Focused tests: not run; no adapter change for this source
- Full tests: not run; no adapter change for this source
- `validate_source.py` result: not run; no active jobs
- UI/API verification: one bounded worker attempt returned `no_concrete_visible_job_cards`
- Public snapshot export: not run

## Outcome

- Final source states: candidate / access unknown / analyzing; bounded attempt failed
- Active jobs after run: 0
- Complete active snapshot: no
- Blocker/risks: the public page responds but the visible HTML adapter cannot observe stable concrete job cards; do not retry without new adapter evidence
- Exact next action: continue with another unfailed source
