# SRC-20260820-honor-campus

- company: 荣耀
- owner: Codex
- state: partial_blocked
- official_url: https://www.honor.com/cn/career/
- campus_url: https://career.honor.com/SU60eea919bef57c1023f6fe78/pb/school.html

## Evidence

荣耀官网招聘页链接到官方 career.honor.com 校园招聘页。公开页面显示“在招职位97个”，可见职位名称、职位类别、工作地点、工作类型和分页，岗位范围为应届生/校园招聘，无登录墙。

## Collection result

- command: `python -m crawler.worker --source honor-campus`
- result: failed at parser gate
- reason: `no_concrete_visible_job_cards`
- accepted jobs: 0

页面通过动态脚本渲染列表，通用 HTML 适配器未得到稳定的具体详情/投递链接。未猜测详情接口或写入不完整岗位，已转专用接口/人工录入队列。
