# SRC-20260820-sugon-campus

- 企业：中科曙光
- 官方归属证据：https://www.sugon.com/about/talents
- 官方校招入口：https://sugon.zhiye.com/
- ATS：北森公开门户，接口为 `/api/Jobad/GetJobAdPageList`。
- 首轮采集：复用 Beisen 适配器，遍历公开分页；发现 179 条，写入 179 条。
- 结果：岗位库新增 179 条，`snapshot_complete=false`。
- 验证：worker 成功，标准化门禁通过；未绕过登录、验证码或访问控制。
