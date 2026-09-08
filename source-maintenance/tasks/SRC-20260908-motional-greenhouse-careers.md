# SRC-20260908-motional-greenhouse-careers

- State: integrated / sampled
- Company: Motional
- Source ID: motional-greenhouse-careers
- Owner/agent: Codex
- Started at: 2026-09-08
- Target scope: campus full-time | campus internship

## Official evidence
- Official company site: https://motional.com/careers (HTTP 200)
- ATS/platform: Greenhouse; public list: https://boards-api.greenhouse.io/v1/boards/motional/jobs?content=true
- Bounded probe: 68 public jobs; explicit Machine Learning Internship and Software Engineer Intern titles observed; no login/CAPTCHA/403/429.

## Collection contract
- Stable source job ID: Greenhouse numeric job ID; returned absolute application URL.
- Intentional cap: max_jobs=20; `snapshot_complete=false`.

## Implementation and validation
- Changed files: config/sources.json; this task file
- Single-source command/validation: worker completed; validate_source.py passed (3 active)
- Outcome: confirmed / reachable / integrated; 3 active jobs; sampled incomplete snapshot
