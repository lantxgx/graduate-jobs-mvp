# SRC-20260820-venustech-campus

- 企业：启明星辰
- 官方归属证据：https://www.venustech.com.cn/new_type/rczp/
- 官方校招入口：https://venustech2.zhiye.com/campus
- ATS：北森（Beisen）公开校园门户，接口为 `/api/Jobad/GetJobAdPageList`。
- 首轮采集：复用 Beisen 适配器，发现 5 条，写入 5 条。
- 结果：岗位库新增 5 条，`snapshot_complete=false`。
- 验证：worker 成功，标准化门禁通过；不绕过登录、验证码或访问控制。
