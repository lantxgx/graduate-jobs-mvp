# SRC-20260906-ximalaya-beisen-internship

- company: 喜马拉雅
- source_id: ximalaya-beisen-internship
- owner: Codex
- status: integrated (bounded public snapshot; not claimed as complete)
- official ownership URL: http://jobs.ximalaya.com/campus
- public listing URL: http://jobs.ximalaya.com/campus
- ATS: Beisen / zhiye.com
- checked_at: 2026-09-06 (+08:00)

## Evidence before collection

- The official recruitment portal publicly separates campus recruitment and internship recruitment. The public Beisen endpoint reported 0 campus roles and 2 internship roles; both internship records exposed concrete titles, Shanghai location, duties, requirements and official detail routes.
- Social-recruitment records were excluded. No login, CAPTCHA, 403, 429, proxy, or access-control bypass was used.
- The actual count is 2, so the source was accepted with `--min-jobs 2` rather than inventing a third job; `snapshot_complete=false` remains in force.

## Result

- Public count: 2 internship listings; 2 normalized active jobs accepted。
- Created: 2; updated: 0; quarantined: 0; deactivated: 0。

## Verification

- `validate_source.py --source-id ximalaya-beisen-internship --min-jobs 2`: passed; both active jobs satisfy the contract。
- Source registry promoted the source to `confirmed / reachable / integrated` after the successful run。
- `python -m unittest discover -s tests -q`: 126 passed。
- `python scripts/export_github_pages.py`: exported 3133 active jobs。

## Next command

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
.\.venv\Scripts\python.exe scripts/export_github_pages.py
```
