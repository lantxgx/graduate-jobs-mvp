# SRC-20260820-hikvision-campus-new

- 公司：海康威视
- 官方入口：https://campushr.hikvision.com/school?schoolType=nozxf&activeTab=0
- 平台：自建招聘门户，公开接口 `/api/search/crsPositionSearch/getPositionByQuery`
- 官方页面公开可访问，无登录、验证码或访问控制绕过。
- 接口报告应届生岗位总数 88，本次按 20 条上限试采并保留 `snapshot_complete=false`。
- 已采集并写入 SQLite：20 条，字段包含岗位、城市、招聘类型、学历要求、职责、任职要求及官方投递链接。
- source id：`hikvision-campus-new`
- 适配器：[hikvision.py](../../crawler/adapters/hikvision.py)
- 前端快照已刷新至 `docs/jobs.json`。
