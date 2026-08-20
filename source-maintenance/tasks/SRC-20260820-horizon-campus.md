# SRC-20260820-horizon-campus

- 企业：地平线
- 官方归属入口：https://horizon-campus.hotjob.cn/
- 官方校招岗位页：https://wecruit.hotjob.cn/SU6409ef49bef57c635fd390a6/pb/school.html?projectCode=103302
- ATS：大易（Hotjob）；公开接口为 `/wecruit/positionInfo/listPosition/SU6409ef49bef57c635fd390a6`，详情接口为 `/wecruit/positionInfo/listPositionDetail/SU6409ef49bef57c635fd390a6`。
- 首轮采集：新增 Hotjob 适配器，分页上限 20 条；发现 20 条，写入 20 条。
- 结果：岗位库新增 20 条，`snapshot_complete=false`。
- 验证：详情包含岗位职责、任职要求、工作地点和官方详情/投递路由；标准化门禁通过。未绕过登录、验证码或访问控制。
