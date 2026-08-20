# SRC-20260820-ccb-campus

- 企业：建设银行
- 官方校招入口：https://job2.ccb.com/cn/job/plan_index.html?planType=XY
- 核验结果：官网校招入口可访问，使用现有 `ccb` 适配器进行一次受控采集。
- 采集结果：0 条合格岗位；worker 返回 `crawl_produced_no_qualified_concrete_jobs`，因此没有写入岗位库，也没有停用历史岗位。
- 失败原因：本轮公开接口未产生同时具备具体岗位、稳定申请链接和必需标准字段的记录。
- 后续：保留失败证据，后续刷新同一官方入口；若岗位详情公开并满足字段门禁，再重新采集。
