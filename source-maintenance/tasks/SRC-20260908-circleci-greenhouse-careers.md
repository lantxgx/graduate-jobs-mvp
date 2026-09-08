# SRC-20260908-circleci-greenhouse-careers

- State: blocked
- Company: CircleCI
- Source ID: circleci-greenhouse-careers
- Owner/agent: Codex
- Official evidence: https://circleci.com/careers/ → public Greenhouse list https://boards-api.greenhouse.io/v1/boards/circleci/jobs?content=true (200, 7 rows; no login/CAPTCHA/403/429).
- Collection: Greenhouse numeric IDs and returned absolute URLs; max_jobs=20; `snapshot_complete=false`.
- Result: `python -m crawler.worker --source circleci-greenhouse-careers` → `crawl_produced_no_qualified_concrete_jobs`; 0 active jobs.
- Outcome: paused; do not retry without new adapter evidence.
