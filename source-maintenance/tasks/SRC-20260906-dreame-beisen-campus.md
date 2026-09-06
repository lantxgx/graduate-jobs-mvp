# SRC-20260906-dreame-beisen-campus

- company: 追觅科技
- source_id: dreame-beisen-campus
- owner: Codex
- status: integrated (bounded public snapshot; not claimed as complete)
- official company URL: https://www.dreame.tech
- public campus listing URL: https://dreame.zhiye.com/campus/jobs
- ATS: Beisen / zhiye.com
- checked_at: 2026-09-06 (+08:00)

## Evidence before collection

- 追觅官网公开可访问；其公开招聘门户标题为“追觅招聘”，校招入口公开提供具体职位列表与详情字段。
- Public Beisen response reported 69 campus/intern listings on the first page probe; no login, CAPTCHA, or access-control bypass was required.
- Reuse `crawler/adapters/beisen.py`; keep `snapshot_complete=false` for this first integration.

## Result

- Public count: 69 listings observed; 69 normalized active jobs accepted.
- Created: 69; updated: 0; quarantined: 0; deactivated: 0.
- The worker observed the reported total through five page requests and did not deactivate prior jobs because `snapshot_complete=false`.

## Verification

- `validate_source.py --source-id dreame-beisen-campus --min-jobs 3`: passed; 69 active jobs and all active-job contract checks passed.
- `python -m unittest discover -s tests -v`: 125 passed.
- `python scripts/export_github_pages.py`: exported 3036 active jobs.

## Next command

```powershell
.\.venv\Scripts\python.exe -m crawler.source_registry --source-file config/sources.json
.\.venv\Scripts\python.exe -m crawler.worker --source dreame-beisen-campus
```
