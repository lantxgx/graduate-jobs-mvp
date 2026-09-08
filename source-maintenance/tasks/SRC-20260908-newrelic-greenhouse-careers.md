# SRC-20260908-newrelic-greenhouse-careers

- State: blocked
- Company: New Relic
- Source ID: newrelic-greenhouse-careers
- Owner/agent: Codex
- Official evidence: https://newrelic.com/about/careers → public Greenhouse list https://boards-api.greenhouse.io/v1/boards/newrelic/jobs?content=true (200, 49 rows; no login/CAPTCHA/403/429).
- Collection: Greenhouse numeric IDs and returned absolute URLs; max_jobs=20; `snapshot_complete=false`.
- Result: current call stopped by cooldown; the source has no accepted active jobs and remains paused after the prior failed run.
- Outcome: do not retry without new adapter evidence.
