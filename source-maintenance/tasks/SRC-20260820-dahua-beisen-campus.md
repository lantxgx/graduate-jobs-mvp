# SRC-20260820-dahua-beisen-campus

- company: 大华股份
- state: integrated_sampled
- official_url: https://dahua.zhiye.com/campus
- adapter: beisen

## Evidence

北森公开招聘门户标题为“浙江大华技术股份有限公司”，校园入口可公开访问并提供具体岗位详情。公开接口为 `https://dahua.zhiye.com/api/Jobad/GetJobAdPageList`，岗位列表和详情均无需登录。

## Collection

- command: `python -m crawler.worker --source dahua-beisen-campus`
- result: success
- jobs_found: 68
- jobs_created: 68
- jobs_updated: 0
- snapshot_complete: false

68 条岗位已通过标准化质量门禁写入 SQLite；本次仍保留非完整快照标记。
