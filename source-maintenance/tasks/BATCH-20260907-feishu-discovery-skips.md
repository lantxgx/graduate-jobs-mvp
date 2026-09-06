# BATCH-20260907-feishu-discovery-skips

本批只记录公开搜索发现的飞书招聘入口。搜索索引不作为官方归属证据；未找到企业官网明确链接或入口已失效的来源均不进入配置，不重复请求。

## 跳过来源

| 入口 | 发现结果 | 决定 |
|---|---|---|
| `rigolportal.jobs.feishu.cn/campus` | 普源精电官网可访问，但首页未发现招聘/校招入口，无法建立官方归属链 | `official_ownership_unverified` |
| `duxiaoman.jobs.feishu.cn/051736` | 度小满官网未发现对应校招入口；搜索结果不足以证明官方归属 | `official_ownership_unverified` |
| `echotech.jobs.feishu.cn/xiaozhao/homepage` | 公开请求返回 HTTP 404 | `stale_public_url` |
| `payermax.jobs.feishu.cn/campus` | 公开请求返回 HTTP 404，企业官网未发现对应校招入口 | `stale_public_url` |
| `modelbest.jobs.feishu.cn/campus` | 公开请求返回 HTTP 404，面壁智能官网未发现对应校招入口 | `stale_public_url` |
| `a9ihi0un9c.jobs.feishu.cn/campus` | 公开请求返回 HTTP 404，无法确认企业归属 | `stale_public_url` |

未调用私有接口、未绕过登录或验证码、未把搜索摘要当作岗位证据。除非出现新的官方入口证据，不再重试这些地址。
