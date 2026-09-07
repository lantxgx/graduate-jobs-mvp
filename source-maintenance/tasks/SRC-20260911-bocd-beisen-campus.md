# SRC-20260911-bocd-beisen-campus

- company: 成都银行
- source: `bocd-beisen-campus`
- status: blocked
- reason_code: crawl_produced_no_qualified_concrete_jobs
- result: the bounded worker produced no qualified concrete campus jobs; no jobs were written
- next action: do not retry unless the public page or adapter contract changes
- public entry: `https://bocd.zhiye.com/campus`
- evidence: public portal title is “成都银行股份有限公司”; no login or CAPTCHA observed.
- ATS: Beisen public portal
- next action: run one bounded worker probe; keep `snapshot_complete=false`.
