# SRC-20260820-netdragon-campus

- company: 网龙
- official_url: https://nd.zhiye.com/campus
- evidence_url: https://nd.zhiye.com/api/Jobad/GetJobAdPageList
- state: integrated
- adapter: beisen

网龙官方校园招聘入口为北森公开门户。接口返回 `Count=5`，分类过滤 `2/3` 后单页完整返回 5 条岗位；所有记录均有稳定 ID、详情路由、地点、职责和要求。Beisen 适配器完成分页闭合并成功写入 5 条岗位，来源配置为 `snapshot_complete=true`。

运行结果：`netdragon-campus`，`jobs_found=5`，`jobs_created=5`。
