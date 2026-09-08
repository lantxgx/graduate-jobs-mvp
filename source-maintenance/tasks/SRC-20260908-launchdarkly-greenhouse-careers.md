# SRC-20260908-launchdarkly-greenhouse-careers

- State: integrated
- Company: LaunchDarkly
- Source ID: launchdarkly-greenhouse-careers
- Owner/agent: Codex
- Official evidence: https://launchdarkly.com/careers/ → public Greenhouse list https://boards-api.greenhouse.io/v1/boards/launchdarkly/jobs?content=true (200; no login/CAPTCHA/403/429).
- Collection: Greenhouse numeric IDs and returned absolute URLs; max_jobs=20; `snapshot_complete=false`.
- Result: `python -m crawler.worker --source launchdarkly-greenhouse-careers` succeeded: 8 found, 8 created, 0 quarantined.
- Validation: active-job contract passed by the successful run; full suite pending batch completion.
- Outcome: official/reachable/integrated; 8 active jobs; keep snapshot incomplete because the source is capped.
