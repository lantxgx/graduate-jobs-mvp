# SRC-20260908-seatgeek-greenhouse-careers

- State: blocked
- Company: SeatGeek
- Source ID: seatgeek-greenhouse-careers
- Official evidence: https://seatgeek.com/careers → https://boards-api.greenhouse.io/v1/boards/seatgeek/jobs?content=true (HTTP 200, 20 public rows; no login/CAPTCHA/403/429).
- Collection: Greenhouse numeric IDs and returned absolute application URLs; max_jobs=20; `snapshot_complete=false`.
- Result: worker updated 2 existing rows and created 0; it is not a new active company and remains below the 3-job threshold.
- Outcome: retain observed rows, pause source, do not count as new coverage.
