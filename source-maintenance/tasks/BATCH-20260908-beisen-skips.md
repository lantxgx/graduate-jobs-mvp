# BATCH-20260908-beisen-skips

本批对 10 个公开北森入口做了一次有界探测。按“难获取就先跳过”的规则，以下 8 家不重复请求，除非页面或适配器契约发生变化：

| 企业 | 来源 | 原因 |
|---|---|---|
| 杰瑞集团 | `jereh-beisen-campus` | `beisen_page_limit_before_source_count` |
| 南方水泥 | `scement4-beisen-campus` | `crawl_produced_no_qualified_concrete_jobs` |
| 中船集团 | `cssc-beisen-campus` | `public_job_page_request_failed` |
| 国新证券 | `crsec-beisen-campus` | `public_job_page_request_failed` |
| 宝龙集团 | `powerlong-beisen-campus` | `public_job_page_request_failed` |
| 新华保险 | `nci-beisen-campus` | `public_job_page_request_failed` |
| 招商船舶 | `cmi-beisen-campus` | `beisen_page_limit_before_source_count` |
| 中机国际工程设计研究院 | `cmie-beisen-campus` | `public_job_page_request_failed` |

三井住友银行（中国）和来伊份各接入 4 个岗位，作为采样接入；两者均未宣称全量覆盖。
