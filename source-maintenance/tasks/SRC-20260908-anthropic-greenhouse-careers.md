# SRC-20260908-anthropic-greenhouse-careers

- State: integrated
- Company: Anthropic
- Source ID: anthropic-greenhouse-careers
- Owner/agent: Codex
- Started at: 2026-09-08
- Target scope: campus full-time | campus internship

## Official evidence
- Official company site: https://www.anthropic.com/careers (HTTP 200)
- ATS/platform: Greenhouse; public list: https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true
- Bounded probe: 588 public jobs observed; no login/CAPTCHA/403/429.

## Collection contract
- Stable source job ID: Greenhouse numeric job ID; detail URL is the returned absolute official application URL.
- Intentional cap: max_jobs=20; `snapshot_complete=false`.

## Implementation and validation
- Changed files: config/sources.json; this task file
- Single-source command: worker completed; 12 accepted/created
- `validate_source.py`: passed after registry promotion
- Outcome: confirmed / reachable / integrated; 12 active jobs; sampled incomplete snapshot
