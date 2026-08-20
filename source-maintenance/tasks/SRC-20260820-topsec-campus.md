# SRC-20260820-topsec-campus

- 企业：天融信
- 官方归属证据：https://www.topsec.com.cn/
- 官方校招入口：https://topsec.zhiye.com/campus/jobs
- ATS：北森（Beisen）公开校园门户，接口为 `/api/Jobad/GetJobAdPageList`。
- 首轮采集：复用 Beisen 适配器，发现 9 条，写入 9 条。
- 结果：岗位库新增 9 条，`snapshot_complete=false`。
- 验证：worker 成功，标准化门禁通过；未绕过登录、验证码或访问控制。
