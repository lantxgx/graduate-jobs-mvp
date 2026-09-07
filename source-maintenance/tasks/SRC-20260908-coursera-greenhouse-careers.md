# SRC-20260908-coursera-greenhouse-careers

- State: integrated
- Company: Coursera
- Source ID: coursera-greenhouse-careers
- Owner/agent: Codex
- Started at: 2026-09-08
- Target scope: campus full-time | campus internship

## Official evidence
- Official company site: https://careers.coursera.com/ (HTTP 200)
- ATS/platform: Greenhouse; public list: https://boards-api.greenhouse.io/v1/boards/coursera/jobs?content=true
- Bounded probe: 23 public jobs observed; no login/CAPTCHA/403/429.

## Collection contract
- Stable source job ID: Greenhouse numeric job ID; returned absolute application URL.
- Intentional cap: max_jobs=20; `snapshot_complete=false`.

## Implementation and validation
- Changed files: config/sources.json; this task file
- Single-source command: worker completed; 8 accepted/created
- `validate_source.py`: passed after registry promotion
- Outcome: confirmed / reachable / integrated; 8 active jobs; sampled incomplete snapshot
