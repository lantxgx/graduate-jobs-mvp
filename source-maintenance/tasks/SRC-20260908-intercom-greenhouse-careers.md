# SRC-20260908-intercom-greenhouse-careers

- State: blocked
- Company: Intercom
- Source ID: intercom-greenhouse-careers
- Owner/agent: Codex
- Started at: 2026-09-08
- Target scope: campus full-time | campus internship

## Baseline
- Registry row/status: new candidate; not previously attempted
- Existing active jobs: 0
- Existing adapter/config: reusable Greenhouse adapter
- Related dirty files: preserve unrelated user changes

## Official evidence
- Official company site: https://www.intercom.com/careers (HTTP 200 in bounded probe)
- Career entry/final URL: https://www.intercom.com/careers
- Ownership evidence URL and visible evidence: official Intercom careers page
- ATS/platform: Greenhouse
- Public list URL: https://boards-api.greenhouse.io/v1/boards/intercom/jobs?content=true
- Concrete detail URL: each returned job's absolute Greenhouse URL
- Access-control signals: no login/CAPTCHA/403/429 observed in bounded probe

## Collection contract
- Listing endpoint/page: Greenhouse jobs API with content=true
- Detail endpoint/page: embedded job content and absolute job URL
- Stable source job ID: Greenhouse numeric job ID
- Pagination/cursor and termination: public board response; initial run intentionally capped by config
- Source-reported total: 130 observed in bounded probe
- Intentional caps: max_jobs=20, max_detail=20 via runner defaults
- Snapshot complete: no
- Completeness evidence: sampled source; not claiming full snapshot

## Implementation and validation
- Changed files: config/sources.json; this task file
- Fixture/tests: existing Greenhouse adapter tests
- Single-source command: worker completed; 2 accepted/created
- jobs_found/created/updated: 2/2/0
- accepted/quarantined: 2/0
- `validate_source.py` result: failed minimum 3-job gate (2 active)
- UI/API verification: API jobs retained
- Public snapshot export: generated with batch export

## Outcome
- Final source states: candidate / reachable / analyzing; paused after one bounded run
- Active jobs after run: 2
- Complete active snapshot: no
- Blocker/risks: full-time roles are collected from the public board; campus-specific filtering is not asserted
- Exact next action: do not retry without new public evidence
