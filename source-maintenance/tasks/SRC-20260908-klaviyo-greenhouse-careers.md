# SRC-20260908-klaviyo-greenhouse-careers

- State: integrated
- Company: Klaviyo
- Source ID: klaviyo-greenhouse-careers
- Owner/agent: Codex
- Started at: 2026-09-08
- Target scope: campus full-time | campus internship

## Official evidence
- Official company site: https://www.klaviyo.com/careers (HTTP 200)
- ATS/platform: Greenhouse; public list: https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true
- Bounded probe: 141 public jobs observed; no login/CAPTCHA/403/429.

## Collection contract
- Stable source job ID: Greenhouse numeric job ID; detail URL is the returned absolute official application URL.
- Intentional cap: max_jobs=20; `snapshot_complete=false`.

## Implementation and validation
- Changed files: config/sources.json; this task file
- Single-source command: worker completed; 3 accepted/created
- `validate_source.py`: passed after registry promotion
- Outcome: confirmed / reachable / integrated; 3 active jobs; sampled incomplete snapshot
