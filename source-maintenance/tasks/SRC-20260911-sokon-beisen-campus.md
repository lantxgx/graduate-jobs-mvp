# SRC-20260911-sokon-beisen-campus

- company: 赛力斯集团
- source: `sokon-beisen-campus`
- status: blocked
- reason_code: beisen_page_limit_before_source_count
- result: one bounded worker probe hit the page limit before the public source count could be reconciled; no jobs were written
- next action: do not retry unless the pagination contract changes
- public entry: `https://sokon.zhiye.com/campus`
- official ownership evidence: 赛力斯官网职业规划页 `https://www.seres.cn/p/career-development.html` 明确链接到 `https://sokon.zhiye.com/`；门户标题为“赛力斯集团招聘门户网”。
- ATS: Beisen public portal
- scope: campus recruitment page; no login or CAPTCHA observed
- next action: run one bounded worker probe; keep `snapshot_complete=false` unless full traversal is proven.
