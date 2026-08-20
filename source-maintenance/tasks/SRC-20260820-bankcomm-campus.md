# 交通银行校园招聘（bankcomm-campus）

- company: 交通银行
- source URL: https://job.bankcomm.com/
- official ownership: 交通银行官方招聘域名
- state: blocked — 2026-08-20

## Evidence

官网首页可访问，但校园路径请求返回 HTTP 403；首页本身是动态应用壳，普通 HTTP 探测未得到公开岗位列表和岗位详情。没有绕过访问控制或猜测接口。

## Result

- accepted jobs: 0
- failure reason: `campus_route_forbidden_or_dynamic_shell_only`
- snapshot_complete: false
- old active jobs changed: no
