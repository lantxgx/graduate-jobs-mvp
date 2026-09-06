# SRC-20260908-gac-toyota-campus

- company: 广汽丰田
- source: `gac-toyota-campus`
- status: integrated
- owner: Codex
- checked_at: 2026-09-08

## Official public evidence

- Official ownership: 广汽集团官网人才页面 `https://www.gac.com.cn/cn/talent#join` links to the 广汽丰田 recruitment portal.
- Career URL: `https://gac-toyota.zhiye.com/campus/jobs`
- ATS evidence: public legacy Beisen/Zhiye server-rendered HTML (`jobsTable`, `zpdetail`, `xiangqinglist`).
- Detail evidence: `https://gac-toyota.zhiye.com/zpdetail/621117741`
- The listing and detail pages are publicly readable without login, CAPTCHA, or access-control bypass.

## Collection result

- The public campus listing currently exposes 1 concrete job; accepting the real count is intentional and does not pad the source.
- Accepted job: `621117741` 仪表板设计工程师（应届可投）; 广州; 全职; 本科及以上.
- `snapshot_complete=false`: this legacy page exposes no reliable total/pagination contract, so the source is integrated but intentionally not claimed complete.
- Required duties and qualifications were present on the detail page.

## Implementation and verification

- Added the bounded `gac_toyota` HTML adapter, sanitized fixture, focused test, registry entry, and enabled source configuration.
- Single-source worker, source validation, full tests, export, and coverage audit are the next verification commands.
- Do not retry this source aggressively if the public page becomes blocked; record the failure and preserve the existing snapshot.
