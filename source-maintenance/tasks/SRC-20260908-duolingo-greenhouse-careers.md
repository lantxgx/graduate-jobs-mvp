# SRC-20260908-duolingo-greenhouse-careers

- State: blocked
- Company: Duolingo
- Source ID: duolingo-greenhouse-careers
- Owner/agent: Codex
- Official evidence: https://careers.duolingo.com/ → public Greenhouse list https://boards-api.greenhouse.io/v1/boards/duolingo/jobs?content=true (200, 89 rows; no login/CAPTCHA/403/429).
- Collection: Greenhouse numeric IDs and returned absolute URLs; max_jobs=20; `snapshot_complete=false`.
- Result: `python -m crawler.worker --source duolingo-greenhouse-careers` → `crawl_produced_no_qualified_concrete_jobs`; 0 active jobs.
- Outcome: paused; do not retry without new adapter evidence.
