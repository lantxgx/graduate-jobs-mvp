# SRC-20260907-insta360-feishu-campus

- company: 影石创新（Insta360）
- source_id: insta360-feishu-campus
- official source: https://www.insta360.com/cn/jobs
- public portal: https://arashivision.jobs.feishu.cn/campus
- state: integrated — bounded sample accepted after a minimal parser repair; snapshot remains incomplete
- evidence: official recruitment page explicitly describes campus recruitment/internship and links the Feishu portal
- failed detail: https://arashivision.jobs.feishu.cn/campus/position/7667853804130650378/detail
- initial result: the first detail exposed a pinned badge and combined `深圳校招正式` metadata; the existing parser rejected the valid shape
- repair: support the documented three-line Feishu header variant without weakening the description/requirements gate
- result: one controlled rerun accepted 10 concrete jobs; all have official detail URLs and required visible description/requirements; `snapshot_complete=false`
- next action: keep the source bounded and sampled; do not claim full portal coverage
