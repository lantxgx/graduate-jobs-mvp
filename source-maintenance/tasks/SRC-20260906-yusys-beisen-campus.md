# SRC-20260906-yusys-beisen-campus

- company: 宇信科技
- source_id: yusys-beisen-campus
- owner: Codex
- status: integrated (bounded public snapshot; not claimed as complete)
- official ownership URL: https://www.yusys.com.cn/join-index.html
- public campus listing URL: https://yusys-campus.zhiye.com/campus/jobs
- ATS: Beisen / zhiye.com
- checked_at: 2026-09-06 (+08:00)

## Evidence before collection

- 宇信科技官网职业发展页公开招聘入口；对应门户标题为“北京宇信科技集团股份有限公司”，校招列表公开可访问。
- Public Beisen response reported 10 campus/intern listings with concrete IDs, locations, employment values and detail routes; no login, CAPTCHA, or bypass was required.
- Reuse `crawler/adapters/beisen.py`; keep `snapshot_complete=false` for the first integration.

## Result

- Public count: 10 listings observed; 10 normalized active jobs accepted.
- Created: 10; updated: 0; quarantined: 0; deactivated: 0.
- The worker completed the reported count through two page requests and preserved incomplete-snapshot protection.

## Verification

- `validate_source.py --source-id yusys-beisen-campus --min-jobs 3`: passed; 10 active jobs and all active-job contract checks passed.
- `python -m unittest discover -s tests -q`: 125 passed.
- `python scripts/export_github_pages.py`: exported 3074 active jobs.

## Next command

```powershell
.\.venv\Scripts\python.exe -m crawler.source_registry --source-file config/sources.json
.\.venv\Scripts\python.exe -m crawler.worker --source yusys-beisen-campus
```
