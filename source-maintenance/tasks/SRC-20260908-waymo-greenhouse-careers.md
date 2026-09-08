# SRC-20260908-waymo-greenhouse-careers

- State: blocked
- Company: Waymo
- Source ID: waymo-greenhouse-careers
- Owner/agent: Codex
- Official evidence: https://waymo.com/careers/ → public Greenhouse list https://boards-api.greenhouse.io/v1/boards/waymo/jobs?content=true (200, 344 rows; no login/CAPTCHA/403/429).
- Collection: Greenhouse numeric IDs and returned absolute URLs; max_jobs=20; `snapshot_complete=false`.
- Result: existing worker failure was `crawl_produced_no_qualified_concrete_jobs`; current call stopped by cooldown. No active jobs accepted.
- Outcome: paused; do not retry without new adapter evidence.
