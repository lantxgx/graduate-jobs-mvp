# SRC-20260820-ctrip-campus

- company: 携程
- official_url: https://careers.ctrip.com/#/campus
- evidence_url: https://careers.ctrip.com/#/campus/jobList
- state: blocked/manual

官方校园招聘页可正常访问并公开展示校园招聘范围。岗位列表接口
`/api/hrrecruit/getJobAd` 本轮只返回 1 条“测试职位（请勿投递）”，且没有其余
可投递岗位。该记录明确不应进入岗位库，因此未写入 SQLite，企业转入手动队列，
待官网发布真实校招岗位后再重试。
