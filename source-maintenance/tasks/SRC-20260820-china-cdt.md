# SRC-20260820-china-cdt

- company: 中国大唐
- state: integrated_manual_review
- official_url: https://zhaopin.china-cdt.com/zpgg_index.html
- adapter: none (custom public portal)

## Evidence

中国大唐官网人才招聘链接指向该官方招聘系统。系统公开提供“校园招聘”分类和招聘公告列表；公告查看页面在当前访问状态下提示内容需要登录。

## Collection

- result: partial_failure
- jobs_found: 0 concrete normalized jobs
- jobs_created: 0
- snapshot_complete: false
- reason: 公开分类/公告不等于逐岗位详情，且详情需要登录；未绕过登录限制，不猜测岗位字段或接口。

## Next action

由开发者通过后台手动录入公开公告中的具体岗位，或在官方提供无需登录的岗位详情后再开发专用适配器。

