# SRC-20260908-chime-greenhouse-careers

- State: blocked
- Company: Chime
- Source ID: chime-greenhouse-careers
- Owner/agent: Codex
- Official evidence: https://www.chime.com/careers/ → public Greenhouse list https://boards-api.greenhouse.io/v1/boards/chime/jobs?content=true (200, 65 rows; no login/CAPTCHA/403/429).
- Collection: Greenhouse numeric IDs and returned absolute URLs; max_jobs=20; `snapshot_complete=false`.
- Result: worker was previously failed with `crawl_produced_no_qualified_concrete_jobs`; current call was stopped by source cooldown. No active jobs accepted.
- Outcome: paused; do not retry without new adapter evidence.
