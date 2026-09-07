# SRC-20260908-roku-greenhouse-careers

- State: blocked
- Company: Roku
- Source ID: roku-greenhouse-careers
- Owner/agent: Codex
- Started at: 2026-09-08
- Target scope: campus full-time | campus internship

## Official evidence
- Official company site: https://www.roku.com/jobs (HTTP 200)
- ATS/platform: Greenhouse; public list: https://boards-api.greenhouse.io/v1/boards/roku/jobs?content=true
- Bounded probe: 252 public jobs observed; no login/CAPTCHA/403/429.

## Collection contract
- Stable source job ID: Greenhouse numeric job ID; detail URL is the returned absolute official application URL.
- Intentional cap: max_jobs=20; `snapshot_complete=false`.

## Implementation and validation
- Changed files: config/sources.json; this task file
- Single-source command: worker produced no qualified concrete jobs
- `validate_source.py`: failed; no active jobs
- Outcome: candidate / reachable / analyzing; paused, do not retry without new evidence
