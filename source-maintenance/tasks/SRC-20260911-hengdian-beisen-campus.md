# SRC-20260911-hengdian-beisen-campus

- company: 横店集团
- source: `hengdian-beisen-campus`
- status: blocked
- reason_code: beisen_page_limit_before_source_count
- result: one bounded worker probe hit the page limit before the public source count could be reconciled; no jobs were written
- next action: do not retry unless the pagination contract changes
- public entry: `https://hengdian.zhiye.com/campus`
- official ownership evidence: 横店集团官网 `https://www.hengdian.com/` directly links to `https://hengdian.zhiye.com/campus` and its social-recruitment counterpart; portal title is “横店集团控股有限公司”。
- ATS: Beisen public portal
- scope: campus recruitment; no login or CAPTCHA observed
- next action: run one bounded worker probe; keep `snapshot_complete=false`.
