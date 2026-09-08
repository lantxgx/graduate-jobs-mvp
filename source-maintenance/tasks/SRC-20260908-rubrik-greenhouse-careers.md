# SRC-20260908-rubrik-greenhouse-careers

- State: blocked
- Company: Rubrik
- Source ID: rubrik-greenhouse-careers
- Owner/agent: Codex
- Official evidence: https://www.rubrik.com/company/careers → public Greenhouse list https://boards-api.greenhouse.io/v1/boards/rubrik/jobs?content=true (200, 139 rows; no login/CAPTCHA/403/429).
- Collection: Greenhouse numeric IDs and returned absolute URLs; max_jobs=20; `snapshot_complete=false`.
- Result: current call stopped by cooldown; the source has no accepted active jobs and remains paused after the prior failed run.
- Outcome: do not retry without new adapter evidence.
