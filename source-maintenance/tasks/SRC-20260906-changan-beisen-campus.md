# SRC-20260906-changan-beisen-campus

- company: 长安汽车
- source_id: changan-beisen-campus
- owner: Codex
- status: integrated (bounded public snapshot; not claimed as complete)
- official ownership URL: https://www.changan.com.cn/recruit/school
- public listing URL: https://changan.zhiye.com/campus/jobs
- ATS: Beisen / zhiye.com
- checked_at: 2026-09-06 (+08:00)

## Evidence before collection

- 长安汽车官网招聘页公开可访问，并指向校园招聘入口；对应北森门户的站点备案信息显示“重庆长安汽车股份有限公司”。
- 北森门户公开提供校园招聘列表页和校园招聘详情页；无需登录、验证码或访问控制绕过。
- 计划使用已有 `crawler/adapters/beisen.py`，首轮最多采集 10 条岗位，`snapshot_complete=false`。

## First run result

- 251 public listings were observed in the bounded public response.
- The worker accepted the source but stopped before writing jobs because 12 observations contain country-only locations such as `海外`/`全国`, which exposed a shared `job_locations.city NOT NULL` normalization bug.
- No Changan jobs were published by that run; prior jobs were not deactivated.

## Minimal repair

- Normalize country/province-only location evidence to `city=""` instead of `None`, preserving the scope without inventing a city.
- Add a regression test for country-only location records, then rerun this single source.

## Final result

- Public count: 251 listings; 251 normalized active jobs after detail/listing field gates.
- Created: 223; updated: 28; quarantined: 0; deactivated: 0.
- Pagination: reported `Count=251`, 14 page requests, unique observations reconciled to 251; the source response ended at the reported count.
- The production configuration remains `snapshot_complete=false` as a conservative first integration setting; no claim of future refresh completeness is made by this task.
- Focused normalization tests passed.

## Verification

- `validate_source.py --source-id changan-beisen-campus --min-jobs 3`: passed; 251 active jobs and all active-job contract checks passed.
- `python -m unittest discover -s tests -v`: 125 passed.
- `python scripts/export_github_pages.py`: exported 2967 active jobs.

## Next command

```powershell
.\.venv\Scripts\python.exe -m crawler.source_registry --source-file config/sources.json
.\.venv\Scripts\python.exe -m crawler.worker --source changan-beisen-campus
```
