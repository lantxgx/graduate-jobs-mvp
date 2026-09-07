# SRC-20260908-lattice-greenhouse-careers

- State: blocked
- Company: Lattice
- Source ID: lattice-greenhouse-careers
- Owner/agent: Codex
- Started at: 2026-09-08
- Target scope: campus full-time | campus internship

## Official evidence
- Official company site: https://lattice.com/careers (HTTP 200)
- ATS/platform: Greenhouse; public list: https://boards-api.greenhouse.io/v1/boards/lattice/jobs?content=true
- Bounded probe: 9 public jobs observed; no login/CAPTCHA/403/429.

## Collection contract
- Stable source job ID: Greenhouse numeric job ID; detail URL is the returned absolute official application URL.
- Intentional cap: max_jobs=20; `snapshot_complete=false`.

## Implementation and validation
- Changed files: config/sources.json; this task file
- Single-source command: worker produced no qualified concrete jobs
- `validate_source.py`: failed; no active jobs
- Outcome: candidate / reachable / analyzing; paused, do not retry without new evidence
