# SRC-20260908-verkada-greenhouse-careers

- State: integrated
- Company: Verkada
- Source ID: verkada-greenhouse-careers
- Owner/agent: Codex
- Started at: 2026-09-08
- Target scope: campus full-time | campus internship

## Official evidence
- Official company site: https://www.verkada.com/careers/ (HTTP 200)
- ATS/platform: Greenhouse; public list: https://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true
- Bounded probe: 290 public jobs observed; no login/CAPTCHA/403/429.

## Collection contract
- Stable source job ID: Greenhouse numeric job ID; returned absolute application URL.
- Intentional cap: max_jobs=20; `snapshot_complete=false`.

## Implementation and validation
- Changed files: config/sources.json; this task file
- Single-source command: worker completed; 16 accepted/created
- `validate_source.py`: passed after registry promotion
- Outcome: confirmed / reachable / integrated; 16 active jobs; sampled incomplete snapshot
