# SRC-20260908-calendly-greenhouse-careers

- State: implementing
- Company: Calendly
- Source ID: calendly-greenhouse-careers
- Owner/agent: Codex
- Started at: 2026-09-08
- Target scope: campus full-time | campus internship

## Official evidence
- Official company site: https://careers.calendly.com/ (HTTP 200)
- ATS/platform: Greenhouse; public list: https://boards-api.greenhouse.io/v1/boards/calendly/jobs?content=true
- Bounded probe: 10 public jobs observed; no login/CAPTCHA/403/429.

## Collection contract
- Stable source job ID: Greenhouse numeric job ID; detail URL is the returned absolute official application URL.
- Intentional cap: max_jobs=20; `snapshot_complete=false`.

## Implementation and validation
- Changed files: config/sources.json; this task file
- Single-source command/validation: pending
- Outcome: pending worker run; do not promote before contract and minimum-job gates pass.
