# SRC-20260820-servyou-campus

- 企业：税友股份（税友软件集团股份有限公司）
- 官方归属证据：https://www.servyou.com.cn/JoinUs/Index/1027506735376922
- 官方校招入口：https://app.mokahr.com/campus-recruitment/servyou/102033/
- ATS：Moka；页面公开 `init-data`，并能通过公开职位详情路由获取具体岗位。
- 首轮采集：现有 Moka 适配器，受控上限 3 条；发现 1 条、写入 1 条。
- 结果：岗位库新增 1 条，`snapshot_complete=false`（页面为当前公开列表的受控采样，后续继续刷新）。
- 验证：worker 成功，岗位具备官方详情/申请链接；未绕过登录、验证码或访问控制。
