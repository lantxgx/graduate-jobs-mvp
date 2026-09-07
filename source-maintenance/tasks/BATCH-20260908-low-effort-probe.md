# BATCH-20260908-low-effort-probe

## 执行结论

本批只复用现有 Moka 适配器，逐个单源执行；未通过具体岗位/字段门禁的来源立即停止，不重复请求。没有新增可计入企业，因此未触发“新增 10 家后推送 GitHub”的发布条件。

## 探测结果

| source_id | 结果 | 原因/说明 |
|---|---|---|
| `huatong-moka-campus` | 暂停 | `crawl_produced_no_qualified_concrete_jobs` |
| `fiberhome-moka-campus` | 暂停 | `crawl_produced_no_qualified_concrete_jobs` |
| `megvii-moka-campus` | 暂停 | `crawl_produced_no_qualified_concrete_jobs` |
| `4paradigm-moka-campus` | 暂停 | `public_job_list_missing` |
| `smartx-moka-campus` | 暂停 | `public_job_list_missing` |
| `zkxx-moka-internship` | 暂停 | `crawl_produced_no_qualified_concrete_jobs` |
| `leyuan-moka-campus` | 暂停 | `public_job_list_missing` |
| `sohu-moka-campus` | 暂停 | `crawl_produced_no_qualified_concrete_jobs` |
| `kingdee-moka-campus` | 已有来源刷新 | 发现 8 条，1 条新增、7 条更新；校验发现 2 条缺少 `requirements`，不计为新增企业，缺字段记录保留在隔离区 |
| `glodon-moka-campus` | 已有来源刷新 | 发现 10 条、0 条新增、10 条更新；不计为新增企业 |
| `transsion-beisen-campus` | 暂停 | `beisen_page_limit_before_source_count` |
| `goodix-beisen-campus` | 暂停 | `public_job_page_request_failed` |
| `360-campus` | 已有来源刷新 | 发现 107 条、0 条新增、107 条更新；不计为新增企业 |
| `kingfa-beisen-campus` | 暂停 | `beisen_page_limit_before_source_count` |
| `cicc-beisen-campus` | 暂停 | `beisen_page_limit_before_source_count` |
| `leapmotor-beisen-campus` | 暂停 | `beisen_page_limit_before_source_count` |
| `tigermed-beisen-campus` | 暂停 | `beisen_page_limit_before_source_count` |
| `starbucks-beisen-campus-new` | 暂停 | `crawl_produced_no_qualified_concrete_jobs` |
| `heytea-beisen-campus` | 暂停 | `beisen_page_limit_before_source_count` |
| `uniqlo-beisen-campus` | 暂停 | `beisen_page_limit_before_source_count` |
| `boe-beisen-campus-new` | 暂停 | `crawl_produced_no_qualified_concrete_jobs` |

## 运行命令

```powershell
python -m crawler.worker --source <source_id>
python C:\Users\lantx\.codex\skills\maintain-campus-job-data\scripts\validate_source.py --project-root . --source-id kingdee-moka-campus --min-jobs 1
```

## 当前状态

- 探测前后企业覆盖：`172/300`，没有新增企业。
- 岗位数：`7692 -> 7695`；变化来自既有来源刷新，不作为企业扩量成果。
- 本轮新增探测均未产生可发布企业；失败来源不再重试。
- 配置审计结果：现有名录中已无“未暂停、无有效岗位、且企业尚未覆盖”的可复用来源；剩余来源均为已有企业刷新、已暂停失败源，或需要新适配器。
- 继续动作：新增公开、可验证且已有适配器的官方来源后再继续；不把搜索结果页、聚合站或社招页面当作岗位来源。
