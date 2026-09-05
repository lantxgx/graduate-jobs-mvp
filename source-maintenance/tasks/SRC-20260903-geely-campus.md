# SRC-20260903-geely-campus

- company: 吉利汽车
- source_id: geely-campus
- official listing URL: https://campus.geely.com/campus-recruitment/geely/78436
- ATS: Moka
- operator: Codex
- status: completed refresh
- checked_at: 2026-09-03T17:07:04+08:00 (+08:00)

## Result

- active jobs after refresh: 32
- newly accepted in this run: 2
- rejected/quarantined: 0 reported by worker
- snapshot completeness: false (source configuration is intentionally bounded)
- roster status: 录入成功

## Commands

```powershell
.\.venv\Scripts\python.exe -m crawler.worker --source geely-campus
.\.venv\Scripts\python.exe scripts\export_github_pages.py
```

## Evidence and limits

The source is the public Moka campus portal configured in `config/sources.json`. The worker completed without an error and the active-job count increased from 30 to 32. This is a refresh, not a claim that every public Geely position was exhaustively traversed; keep `snapshot_complete=false` until pagination completeness is proven.
