# SRC-20260906-luyuan-beisen-campus

- company: 浙江绿源电动车有限公司
- source_id: luyuan-beisen-campus
- owner: Codex
- status: integrated (bounded public snapshot; not claimed as complete)
- official ownership URL: https://www.luyuan.cn/
- public campus listing URL: https://luyuan.zhiye.com/campus/jobs
- ATS: Beisen / zhiye.com
- checked_at: 2026-09-06 (+08:00)

## Evidence before collection

- 绿源官网公开链接到 `https://luyuan.zhiye.com/`；公开门户元数据显示租户为 `luyuan`，公司名为“浙江绿源电动车有限公司”。
- 公开校招列表无需登录、验证码或访问控制绕过；Beisen 列表接口返回 37 个校招/实习岗位，包含稳定岗位 ID、岗位名称、地点和招聘类型。
- 复用 `crawler/adapters/beisen.py`；首次接入保持 `snapshot_complete=false`。

## Result

- Public count: 37 listings observed; 37 normalized active jobs accepted。
- Created: 37; updated: 0; quarantined: 0; deactivated: 0。
- Worker traversed the reported first-page sample and preserved incomplete-snapshot protection; this is not claimed as a complete snapshot。

## Verification

- `validate_source.py --source-id luyuan-beisen-campus --min-jobs 3`: passed; 37 active jobs and all active-job contract checks passed。
- Source registry reconciliation promoted the source to `confirmed / reachable / integrated` after the successful run。
- `python -m unittest discover -s tests -q`: 125 passed。
- `python scripts/export_github_pages.py`: exported 3111 active jobs。

## Next command

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
.\.venv\Scripts\python.exe scripts/export_github_pages.py
```
