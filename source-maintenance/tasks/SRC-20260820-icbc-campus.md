# 工商银行校园招聘（icbc-campus）

- company: 工商银行
- source URL: https://job.icbc.com.cn/pc/index.html
- official ownership: 工商银行官方招聘域名 `job.icbc.com.cn`
- state: blocked — 2026-08-20

## Evidence

官方 PC 招聘 SPA 可公开打开。正常页面脚本暴露岗位列表与详情接口：

- `POST https://job.icbc.com.cn/icbc/trmo/post/qryPostList`
- `POST https://job.icbc.com.cn/icbc/trmo/post/qryPostById`

在不登录、不绕过安全控制的情况下，岗位列表接口对公开请求返回 `retCode=90`（系统繁忙），没有公开岗位列表或岗位详情可供核验。因此没有写入岗位库。

## Result

- accepted jobs: 0
- failure reason: `public_post_api_returns_system_busy`
- snapshot_complete: false
- old active jobs changed: no

后续仅在官方接口恢复公开返回具体岗位时重试，不猜测岗位字段或构造岗位数据。
