# SRC-20260911-cscec-beisen-campus

- company: 中国建筑
- source: `cscec-beisen-campus`
- status: blocked
- reason_code: public_job_page_request_failed
- result: one bounded worker probe could not retrieve the public job page; no jobs were written
- next action: do not retry unless the public contract changes
- public entry: `https://cscec.zhiye.com/campus`
- official ownership evidence: 中国建筑官网 `https://www.cscec.com/` directly links to `https://recruit.cscec.com/recruit#/`; the public Beisen tenant is titled “中国建筑高校毕业生接收考试网网申系统--校园招聘”。
- ATS: Beisen public portal
- scope: campus recruitment; no login or CAPTCHA observed
- next action: run one bounded worker probe; keep `snapshot_complete=false`.
