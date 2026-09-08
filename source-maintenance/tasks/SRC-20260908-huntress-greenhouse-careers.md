# SRC-20260908-huntress-greenhouse-careers

- State: integrated / sampled
- Company: Huntress
- Source ID: huntress-greenhouse-careers
- Owner/agent: Codex
- Started at: 2026-09-08
- Target scope: campus full-time | campus internship

## Official evidence
- Official company site: https://www.huntress.com/careers (HTTP 200)
- ATS/platform: Greenhouse; public list: https://boards-api.greenhouse.io/v1/boards/huntress/jobs?content=true
- Bounded probe: 40 public jobs observed; no login/CAPTCHA/403/429.

## Collection contract
- Stable source job ID: Greenhouse numeric job ID; returned absolute application URL.
- Intentional cap: max_jobs=20; `snapshot_complete=false`.

## Implementation and validation
- Changed files: config/sources.json; this task file
- Single-source command/validation: worker completed; validate_source.py passed (16 active)
- Outcome: confirmed / reachable / integrated; 16 active jobs; sampled incomplete snapshot
