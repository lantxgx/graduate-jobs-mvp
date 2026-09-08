# SRC-20260908-riotgames-greenhouse-careers

- State: blocked / paused
- Company: Riot Games
- Source ID: riotgames-greenhouse-careers
- Owner/agent: Codex
- Started at: 2026-09-08
- Target scope: campus full-time | campus internship

## Official evidence
- Official company site: https://www.riotgames.com/en/work-with-us (HTTP 200)
- ATS/platform: Greenhouse; public list: https://boards-api.greenhouse.io/v1/boards/riotgames/jobs?content=true
- Bounded probe: 163 public jobs; explicit Game Production Intern and Research Intern titles observed; no login/CAPTCHA/403/429.

## Collection contract
- Stable source job ID: Greenhouse numeric job ID; returned absolute application URL.
- Selection: title keywords for intern/early career/graduate/student; max_jobs=20; `snapshot_complete=false`.

## Implementation and validation
- Changed files: config/sources.json; this task file
- Single-source command/validation: bounded worker attempt completed; only 1 qualified active job
- Outcome: candidate / reachable / analyzing; paused to avoid repeated retries; resume only with new evidence or adapter change
