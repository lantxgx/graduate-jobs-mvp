# SRC-20260908-muckrack-greenhouse-careers

- State: blocked
- Company: Muck Rack
- Source ID: muckrack-greenhouse-careers
- Owner/agent: Codex
- Official evidence: https://muckrack.com/careers → public Greenhouse list https://boards-api.greenhouse.io/v1/boards/muckrack/jobs?content=true (200, 9 rows; no login/CAPTCHA/403/429).
- Collection: Greenhouse numeric IDs and returned absolute URLs; max_jobs=20; `snapshot_complete=false`.
- Result: current call stopped by cooldown; the source has no accepted active jobs and remains paused after the prior failed run.
- Outcome: do not retry without new adapter evidence.
