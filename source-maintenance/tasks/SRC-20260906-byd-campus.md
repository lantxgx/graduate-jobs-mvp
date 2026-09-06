# SRC-20260906-byd-campus

- company: 比亚迪
- source_id: byd-campus
- owner: Codex
- status: integrated (bounded public snapshot; not claimed as complete)
- official ownership URL: https://job.byd.com/
- public campus listing URL: https://job.byd.com/portal/pc/#/school/schoolPositionList
- ATS: BYD official recruitment portal
- checked_at: 2026-09-06 (+08:00)

## Evidence before collection

- `https://job.byd.com/` is the company-controlled “比亚迪招聘” site and visibly links to “校园招聘”。
- The normal campus page exposes `POST /portal/api/portal-api/schoolPortal/queryPositionList`; the 2027 graduate channel reported 386 listings. Each listing has a stable outer ID and the public `GET /portal/api/portal-api/schoolPortal/queryPosition` detail response contains concrete duties, requirements, degree, major, location and inner position IDs。
- No login, CAPTCHA, 403, 429, proxy, or access-control bypass was used。
- Added a bounded BYD adapter; first integration remains `snapshot_complete=false` because only 20 detail records were collected from a reported 386-listing source。

## Result

- Public reported count: 386 graduate listings; bounded sample: 20 concrete detail records accepted。
- Created: 20; updated: 0; quarantined: 0; deactivated: 0。
- The first HTTP implementation timed out during detail fan-out and wrote no jobs; it was replaced with the verified browser request context before the single retry. The successful run then passed all gates。

## Verification

- `validate_source.py --source-id byd-campus --min-jobs 3`: passed; 20 active jobs and all active-job contract checks passed。
- `python -m unittest tests.test_byd_adapter tests.test_adapter_registry -v`: 3 passed。
- `python -m unittest discover -s tests -q`: 126 passed。
- `python scripts/export_github_pages.py`: exported 3131 active jobs。

## Next command

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
.\.venv\Scripts\python.exe scripts/export_github_pages.py
```
