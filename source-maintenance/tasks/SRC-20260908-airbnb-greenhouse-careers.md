# SRC-20260908-airbnb-greenhouse-careers

- State: blocked
- Company: Airbnb
- Source ID: airbnb-greenhouse-careers
- Owner/agent: Codex
- Official evidence: https://careers.airbnb.com/ → public Greenhouse list https://boards-api.greenhouse.io/v1/boards/airbnb/jobs?content=true (200, 167 rows; no login/CAPTCHA/403/429).
- Collection: Greenhouse numeric IDs and returned absolute URLs; max_jobs=20; `snapshot_complete=false`.
- Result: worker was previously failed with `crawl_produced_no_qualified_concrete_jobs`; current call was stopped by source cooldown. No active jobs accepted.
- Outcome: paused; do not retry without new adapter evidence.
