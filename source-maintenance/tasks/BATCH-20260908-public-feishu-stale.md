# BATCH-20260908-public-feishu-stale

本批只对搜索发现、尚未进入来源配置的飞书校招入口做一次公开 GET 探测。搜索索引不作为官方归属证据；入口返回 404 时不猜测路径、不注册来源、不写入岗位。

| 候选入口 | 结果 | 决策 |
|---|---|---|
| `honycapital.jobs.feishu.cn/campus` | HTTP 404 | 跳过，不重试 |
| `huanle.jobs.feishu.cn/campus/m/` | HTTP 404 | 跳过，不重试 |
| `jzyxgames.jobs.feishu.cn/campus` | HTTP 404 | 跳过，不重试 |
| `maimai.jobs.feishu.cn/campus` | HTTP 404 | 跳过，不重试 |
| `moonton.jobs.feishu.cn/campus` | HTTP 404 | 跳过，不重试 |
| `rigolportal.jobs.feishu.cn/campus/` | HTTP 404 | 跳过，不重试 |
| `yesv-desaysv.jobs.feishu.cn/campus/` | HTTP 404 | 跳过，不重试 |

未取得官方归属链、公开岗位列表或具体详情，未修改 `config/sources.json`，未写入岗位库。后续只有企业官网出现新的可访问招聘链接时才重新核验。
