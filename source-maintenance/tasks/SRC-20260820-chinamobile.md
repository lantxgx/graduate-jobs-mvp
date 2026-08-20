# SRC-20260820-chinamobile

- company: 中国移动
- state: partial_blocked
- official_url: https://job.10086.cn/personal/job/

中国移动官方招聘网站公开提供职位列表和“校园招聘”筛选项。页面通过 `/job-app/job/search.do` 等接口加载数据，并要求动态 digest/conversationId 签名；项目当前没有该专用适配器，未猜测签名或绕过控制，转专用接口/人工录入。
