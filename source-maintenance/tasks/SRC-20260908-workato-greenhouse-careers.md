# SRC-20260908-workato-greenhouse-careers

- State: blocked / paused
- Company: Workato
- Source ID: workato-greenhouse-careers
- Owner/agent: Codex
- Started at: 2026-09-08
- Target scope: campus full-time | campus internship

## Official evidence
- Official company site: https://www.workato.com/careers (HTTP 200)
- ATS/platform: Greenhouse; public list: https://boards-api.greenhouse.io/v1/boards/workato/jobs?content=true
- Bounded probe: 100 public jobs observed; no login/CAPTCHA/403/429.

## Collection contract
- Stable source job ID: Greenhouse numeric job ID; returned absolute application URL.
- Intentional cap: max_jobs=20; `snapshot_complete=false`.

## Implementation and validation
- Changed files: config/sources.json; this task file
- Single-source command/validation: bounded worker attempt completed; below the 3-job quality gate
- Outcome: candidate / reachable / analyzing; paused to avoid repeated retries; resume only with new evidence or adapter change
