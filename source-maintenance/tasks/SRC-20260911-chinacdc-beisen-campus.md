# SRC-20260911-chinacdc-beisen-campus

- company: 建发集团
- source: `chinacdc-beisen-campus`
- status: blocked
- reason_code: public_job_page_request_failed
- result: one bounded worker probe could not retrieve the public job page; no jobs were written
- next action: do not retry unless the public contract changes
- public entry: `https://chinacdc.zhiye.com/campus`
- official ownership evidence: 建发集团官网 `https://www.chinacdc.com/` directly links to campus, internship, and social recruitment portals under `chinacdc.zhiye.com`; portal title is “建发集团”。
- ATS: Beisen public portal
- scope: campus recruitment; no login or CAPTCHA observed
- next action: run one bounded worker probe; keep `snapshot_complete=false`.
