# SRC-20260820-cainiao-campus

- company: 菜鸟网络
- source_id: alibaba-cainiao-campus
- source_url: https://campus-talent.alibaba.com/campus/index
- state: integrated (sampled)

菜鸟岗位在阿里巴巴官方校园招聘门户的业务单元中公开列出。适配器按
`circleNames` 中的“菜鸟”做证据约束，并遍历官方分页直到取得 10 个具体详情。
10 个岗位全部通过质量门禁并写入 SQLite；门户仍显示分页总量，故快照暂不标记完整。
