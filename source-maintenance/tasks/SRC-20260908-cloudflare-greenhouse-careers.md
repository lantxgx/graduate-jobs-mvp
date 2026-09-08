# SRC-20260908-cloudflare-greenhouse-careers

- State: blocked
- Company: Cloudflare
- Source ID: cloudflare-greenhouse-careers
- Owner/agent: Codex
- Official evidence: https://www.cloudflare.com/careers/jobs/ → public Greenhouse list https://boards-api.greenhouse.io/v1/boards/cloudflare/jobs?content=true (200, 336 rows; no login/CAPTCHA/403/429).
- Collection: title filter for intern/new grad/graduate; max_jobs=20; `snapshot_complete=false`.
- Result: `python -m crawler.worker --source cloudflare-greenhouse-careers` → `crawl_produced_no_qualified_concrete_jobs`; 0 active jobs.
- Outcome: paused; do not retry without new adapter evidence.
