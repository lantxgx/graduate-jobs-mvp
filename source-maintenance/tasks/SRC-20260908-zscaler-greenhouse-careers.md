# SRC-20260908-zscaler-greenhouse-careers

- State: integrated / sampled
- Company: Zscaler
- Source ID: zscaler-greenhouse-careers
- Owner/agent: Codex
- Started at: 2026-09-08
- Target scope: campus full-time | campus internship

## Official evidence
- Official company site: https://www.zscaler.com/careers (HTTP 200)
- ATS/platform: Greenhouse; public list: https://boards-api.greenhouse.io/v1/boards/zscaler/jobs?content=true
- Bounded probe: 363 public jobs observed; no login/CAPTCHA/403/429.

## Collection contract
- Stable source job ID: Greenhouse numeric job ID; returned absolute application URL.
- Intentional cap: max_jobs=20; `snapshot_complete=false`.

## Implementation and validation
- Changed files: config/sources.json; this task file
- Single-source command/validation: worker completed; validate_source.py passed (7 active)
- Outcome: confirmed / reachable / integrated; 7 active jobs; sampled incomplete snapshot
