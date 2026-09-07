# BATCH-20260908-public-tenant-skips

对全新、尚未进入来源配置的北森租户别名做一次极短公开入口探测：

| 候选企业 | 探测入口 | 结果 | 决策 |
|---|---|---|---|
| 瑞幸 | `https://luckin.zhiye.com/campus` | HTTP 200，但页面标题为 `Not Found` | 跳过，不重试 |
| 伊利 | `https://yili.zhiye.com/campus` | HTTP 200，但页面标题为 `Not Found` | 跳过，不重试 |
| 立讯精密 | `https://luxshare.zhiye.com/campus` | HTTP 200，但页面标题为 `Not Found` | 跳过，不重试 |

这只是公开入口可达性探测，未确认到官方招聘列表、具体岗位或详情，因此未写入来源配置，也未写入岗位库。未使用登录、验证码、代理或访问控制绕过。
