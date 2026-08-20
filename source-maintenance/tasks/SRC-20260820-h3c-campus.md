# SRC-20260820-h3c-campus

- 企业：新华三
- 官方归属证据：https://www.h3c.com/cn/About_H3C/JOB/Campus_Recruitment/
- 官方校招入口：https://h3c.zhiye.com/Campus
- ATS：北森（Beisen）公开校园门户，接口为 `/api/Jobad/GetJobAdPageList`。
- 首轮采集：复用 Beisen 适配器，受控分页；发现 78 条，写入 78 条。
- 结果：岗位库新增 78 条，`snapshot_complete=false`。
- 验证：worker 成功，标准化门禁通过；未绕过登录、验证码或访问控制。
