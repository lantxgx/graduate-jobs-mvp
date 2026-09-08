# SRC-20260908-acquia-greenhouse-careers

- State: blocked
- Company: Acquia
- Source ID: acquia-greenhouse-careers
- Official evidence: https://www.acquia.com/careers → https://boards-api.greenhouse.io/v1/boards/acquia/jobs?content=true (HTTP 200, 11 public rows; no login/CAPTCHA/403/429).
- Collection: Greenhouse numeric IDs and returned absolute application URLs; max_jobs=20; `snapshot_complete=false`.
- Result: first write attempt stopped on `sqlite3.OperationalError: database is locked`; no accepted active jobs. No retry performed.
- Outcome: paused; manual database reconciliation is required before any future attempt.
