# SRC-20260908-roblox-greenhouse-careers

- State: blocked
- Company: Roblox
- Source ID: roblox-greenhouse-careers
- Owner/agent: Codex
- Started at: 2026-09-08
- Target scope: campus full-time | campus internship

## Official evidence
- Official company site: https://careers.roblox.com/ (HTTP 200)
- ATS/platform: Greenhouse; public list: https://boards-api.greenhouse.io/v1/boards/roblox/jobs?content=true
- Bounded probe: 231 public jobs; explicit Early Career and Intern titles observed; no login/CAPTCHA/403/429.

## Collection contract
- Stable source job ID: Greenhouse numeric job ID; returned absolute application URL.
- Selection: title keywords for intern/early career/graduate/student; max_jobs=20; `snapshot_complete=false`.

## Implementation and validation
- Changed files: config/sources.json; this task file
- Single-source command/validation: `python -m crawler.worker --source roblox-greenhouse-careers` → `crawl_produced_no_qualified_concrete_jobs`.
- Outcome: candidate / reachable / analyzing; paused, do not retry without new evidence.
- Exact next action: none until adapter evidence changes.
