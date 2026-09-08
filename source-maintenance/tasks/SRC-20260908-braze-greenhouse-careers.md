# SRC-20260908-braze-greenhouse-careers

- State: integrated / sampled
- Company: Braze
- Source ID: braze-greenhouse-careers
- Owner/agent: Codex
- Started at: 2026-09-08
- Target scope: campus full-time | campus internship

## Official evidence
- Official company site: https://www.braze.com/company/careers (HTTP 200)
- ATS/platform: Greenhouse; public list: https://boards-api.greenhouse.io/v1/boards/braze/jobs?content=true
- Bounded probe: 282 public jobs observed; no login/CAPTCHA/403/429.

## Collection contract
- Stable source job ID: Greenhouse numeric job ID; returned absolute application URL.
- Intentional cap: max_jobs=20; `snapshot_complete=false`.

## Implementation and validation
- Changed files: config/sources.json; this task file
- Single-source command/validation: worker completed; validate_source.py passed (8 active)
- Outcome: confirmed / reachable / integrated; 8 active jobs; sampled incomplete snapshot
