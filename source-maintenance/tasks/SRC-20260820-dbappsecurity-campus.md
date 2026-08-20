# SRC-20260820-dbappsecurity-campus

- 企业：安恒信息
- 官方校招入口：https://ahxz.dbappsecurity.com.cn/campus
- 页面类型：北森（Beisen）公开招聘门户；页面公开接口为 `/api/Jobad/GetJobAdPageList`。
- 首轮采集：复用 Beisen 适配器，受控分页；发现 38 条，写入 38 条。
- 结果：岗位库新增 38 条，`snapshot_complete=false`。
- 验证：worker 成功，岗位详情和申请链接通过标准化门禁；未绕过登录、验证码或访问控制。
