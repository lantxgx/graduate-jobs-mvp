# 农业银行校园招聘（abchina-campus）

- company: 农业银行
- source URL: https://career.abchina.com/
- official ownership: 农业银行官方招聘域名及 CDN 页面
- state: blocked — 2026-08-20

## Evidence

官方入口可访问并跳转到 `/build/index.html` 动态应用。页面公开 HTML 只提供应用壳；岗位数据由前端运行时请求并带会话/动态安全参数。对公开页面进行普通 HTTP 探测未获得可核验的岗位列表与详情，未尝试绕过会话、签名或安全控制。

## Result

- accepted jobs: 0
- failure reason: `public_job_data_requires_session_or_dynamic_request`
- snapshot_complete: false
- old active jobs changed: no

待能通过正常公开页面稳定取得具体岗位详情后再接入。
