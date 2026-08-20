# SRC-20260820-tencent-cloud-moka-campus

## 官网核验

- 公司：腾讯云智（云智研发公司）
- 官方校招入口：https://app-tc.mokahr.com/campus-recruitment/csig/20001
- 页面公开可访问：是（HTTP 200）
- 平台：Moka
- Moka 租户证据：`orgId=csig`、`siteId=20001`；公开请求 `/api/outer/ats-apply/website/jobs/module`
- 详情路由：页面公开 hash 路由 `#/job/<jobId>`，由岗位列表 ID 关联
- 登录/验证码/403/429：未遇到

## 试采结果

公开接口报告 2 条岗位，分页边界已返回完整（`jobStats.total=2`）。两条均为实习性质，按项目规范标准化为 `实习`：

| 岗位 | 城市 | 官方投递链接 |
|---|---|---|
| 行政实习生 | 中国 / 陕西 / 西安市 | https://app-tc.mokahr.com/campus-recruitment/csig/20001#/job/1bb03c5e-6a31-4f5a-867d-a4fb08641b34 |
| (日常实习生)策划/运营产品实习生 腾讯云音视频PaaS | 中国 / 陕西 / 西安市 | https://app-tc.mokahr.com/campus-recruitment/csig/20001#/job/f335730e-e83b-46af-9fc1-74fd05986803 |

详情页公开渲染了职位描述、任职要求和招聘类型；未对学历或专业做推断，缺失字段保持为空/原文要求。

## 实施结果

- source id：`tencent-cloud-moka-campus`
- 适配器：`crawler/adapters/moka.py`
- 运行：`$env:CRAWL_MIN_INTERVAL_SECONDS='0'; python -m crawler.worker --source tencent-cloud-moka-campus`
- jobs_found：2；jobs_created：2；jobs_updated：0；deactivated：0
- `snapshot_complete=false`（后续仍需定期复核，避免不完整采集下线旧岗位）
- 数据已写入 SQLite `jobs`，前端导出可通过标准导出脚本刷新

## 后续

可复用该适配器接入其他已核验 Moka 租户（吉利、金山软件等），但必须先确认公开列表接口返回总数和至少一条可访问详情页，再将来源加入配置。
