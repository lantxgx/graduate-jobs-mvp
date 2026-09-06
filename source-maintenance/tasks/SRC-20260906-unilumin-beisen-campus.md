# SRC-20260906-unilumin-beisen-campus

- company: 洲明科技
- source_id: unilumin-beisen-campus
- owner: Codex
- status: integrated (bounded public snapshot; not claimed as complete)
- official ownership URL: https://cn.unilumin.com/about/recruit
- public campus listing URL: https://unilumin.zhiye.com/campus/jobs
- ATS: Beisen / zhiye.com
- checked_at: 2026-09-06 (+08:00)

## Evidence before collection

- 洲明科技官网公开“人才招聘”入口，直接链接到 `https://unilumin.zhiye.com/`。
- Public Beisen response reported 28 campus/intern listings with concrete IDs, locations, employment values and detail routes; no login, CAPTCHA, or bypass was required.
- Reuse `crawler/adapters/beisen.py`; keep `snapshot_complete=false` for the first integration.

## Result

- Public count: 28 listings observed; 28 normalized active jobs accepted.
- Created: 28; updated: 0; quarantined: 0; deactivated: 0.
- The worker completed the reported count through three page requests and preserved incomplete-snapshot protection.

## Verification

- `validate_source.py --source-id unilumin-beisen-campus --min-jobs 3`: passed; 28 active jobs and all active-job contract checks passed.
- `python -m unittest discover -s tests -q`: 125 passed.
- `python scripts/export_github_pages.py`: exported 3064 active jobs.

## Next command

```powershell
.\.venv\Scripts\python.exe -m crawler.source_registry --source-file config/sources.json
.\.venv\Scripts\python.exe -m crawler.worker --source unilumin-beisen-campus
```
