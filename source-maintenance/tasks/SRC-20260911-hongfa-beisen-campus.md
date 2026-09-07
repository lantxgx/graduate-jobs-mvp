# SRC-20260911-hongfa-beisen-campus

- company: 宏发股份
- source: `hongfa-beisen-campus`
- status: blocked
- reason_code: public_job_page_request_failed
- result: one bounded worker probe could not retrieve the public job page; no jobs were written
- next action: do not retry unless the public contract changes
- public entry: `https://hongfa.zhiye.com/campus`
- evidence: public portal title is “宏发股份官方招聘招聘系统--校园招聘”; the company is a publicly identified official recruitment tenant. No login or CAPTCHA observed.
- ATS: Beisen public portal
- next action: run one bounded worker probe; keep `snapshot_complete=false`.
