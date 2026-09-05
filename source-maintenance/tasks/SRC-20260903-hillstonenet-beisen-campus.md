# SRC-20260903-hillstonenet-beisen-campus

- company: 山石网科
- owner: Codex
- source: https://hillstonenet.zhiye.com/campus?c=6401
- adapter: beisen
- state: running
- scope: campus recruitment only; public Beisen listing and detail pages
- baseline: 2026-09-03 audit showed 62 active-job companies, 2529 active jobs

## Evidence and execution

Official ownership and campus scope must be verified from the public source before promotion. Run one bounded source worker, then validate the normalized fields and preserve any quarantine observations. Do not deactivate prior jobs from an incomplete snapshot.

## Result

- 2026-09-03 bounded refresh: 3 jobs found, 0 created, 3 updated, 0 deactivated.
- Public JSON endpoints observed through the existing Beisen adapter; source remained `snapshot_complete=false` because the configured run is bounded.
- `validate_source.py --min-jobs 3`: passed; all active-job contract gates passed.
- Public snapshot exported and deployment data synchronized to the server.
