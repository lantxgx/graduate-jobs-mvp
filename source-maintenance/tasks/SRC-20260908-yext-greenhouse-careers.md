# SRC-20260908-yext-greenhouse-careers

- State: blocked
- Company: Yext
- Source ID: yext-greenhouse-careers
- Official evidence: https://www.yext.com/careers → https://boards-api.greenhouse.io/v1/boards/yext/jobs?content=true (HTTP 200, 22 public rows; no login/CAPTCHA/403/429).
- Collection: Greenhouse numeric IDs and returned absolute application URLs; max_jobs=20; `snapshot_complete=false`.
- Result: worker succeeded with 2 found, 2 created, 0 quarantined; below the 3-job integration threshold.
- Outcome: retain 2 observed jobs, pause source, do not retry without new evidence.
