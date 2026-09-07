# SRC-20260911-genertec-beisen-campus

- company: 通用技术集团
- source: `genertec-beisen-campus`
- status: blocked
- reason_code: beisen_page_limit_before_source_count
- result: one bounded worker probe hit the page limit before the public source count could be reconciled; no jobs were written
- next action: do not retry unless the pagination contract changes
- public entry: `https://genertec.zhiye.com/campus`
- evidence: public portal title identifies “通用技术集团招聘门户”; no login or CAPTCHA observed.
- ATS: Beisen public portal
- next action: run one bounded worker probe; keep `snapshot_complete=false`.
