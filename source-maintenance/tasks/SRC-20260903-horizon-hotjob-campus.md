# SRC-20260903-horizon-hotjob-campus

- company: 地平线
- owner: Codex
- source: https://wecruit.hotjob.cn/SU6409ef49bef57c635fd390a6/pb/school.html?projectCode=103302
- adapter: hotjob
- state: running
- scope: campus recruitment only; public HotJob listing and detail pages
- baseline: 62 active-job companies, 2529 active jobs

## Evidence and execution

Verify official ownership and campus scope from the public source. Run one bounded worker, validate the active-job contract, and preserve quarantine observations. Keep `snapshot_complete=false` unless all public pagination is proven exhausted.

## Result

- 2026-09-03 refresh: 20 jobs found, 0 created, 20 updated, 0 deactivated.
- `validate_source.py --min-jobs 3`: passed; 21 active jobs satisfy the active-job contract.
- Snapshot remains bounded (`snapshot_complete=false`); public snapshot and server database were synchronized.
