# SRC-20260820-sensetime-campus

- 企业：商汤科技
- 官方招聘入口：https://hr.sensetime.com/campus
- 官方校招投递门户：https://hr-jobs.sensetime.com/edu/
- ATS：商汤官方公共 ATS；公开页面正常加载岗位搜索接口 `/api/v1/search/job/posts`，由页面正常生成请求签名。
- 首轮采集：新增浏览器响应适配器，限制 10 条；发现 10 条，写入 10 条。
- 结果：岗位库新增 10 条，`snapshot_complete=false`。
- 验证：公开接口响应包含职责、要求、招聘类型、城市和岗位 ID；使用官方详情路由作为投递链接。未绕过登录、验证码或访问控制。
