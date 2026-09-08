# SRC-20260908-khanacademy-greenhouse-careers

- State: integrated / sampled
- Company: Khan Academy
- Source ID: khanacademy-greenhouse-careers
- Owner/agent: Codex
- Started at: 2026-09-08
- Target scope: campus full-time | campus internship

## Official evidence
- Official company site: https://www.khanacademy.org/careers (HTTP 200)
- ATS/platform: Greenhouse; public list: https://boards-api.greenhouse.io/v1/boards/khanacademy/jobs?content=true
- Bounded probe: 23 public jobs observed; no login/CAPTCHA/403/429.

## Collection contract
- Stable source job ID: Greenhouse numeric job ID; returned absolute application URL.
- Intentional cap: max_jobs=20; `snapshot_complete=false`.

## Implementation and validation
- Changed files: config/sources.json; this task file
- Single-source command/validation: worker completed; validate_source.py passed (12 active)
- Outcome: confirmed / reachable / integrated; 12 active jobs; sampled incomplete snapshot
