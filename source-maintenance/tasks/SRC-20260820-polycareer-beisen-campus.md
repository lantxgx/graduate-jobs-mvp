# SRC-20260820-polycareer-beisen-campus

- company: 保利集团
- state: integrated_sampled
- official_url: https://www.poly.com.cn/poly/rlzy/rczp/A044008002Gone1.html
- career_url: https://polycareer.zhiye.com/campus
- adapter: beisen

## Evidence

保利集团官网“人才招聘”页面公开链接到 `https://polycareer.zhiye.com/campus` 校园招聘入口。该北森门户公开展示校园招聘分类、岗位列表和岗位详情，未要求登录或验证码。

## Collection

- command: `python -m crawler.worker --source polycareer-beisen-campus`
- result: success
- jobs_found: 12
- jobs_created: 12
- jobs_updated: 0
- snapshot_complete: false
- endpoint_seen: `https://polycareer.zhiye.com/api/Jobad/GetJobAdPageList`

12 条岗位已通过标准化质量门禁写入 SQLite；首次接入保留非完整快照标记。

