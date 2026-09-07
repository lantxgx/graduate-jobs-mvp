# BATCH-20260908-greenhouse-probes

本批只处理企业官方 Careers 页面明确链接的 Greenhouse 公共岗位板，并复用现有适配器。

| 企业 | 官方证据 | 结果 | 决策 |
|---|---|---|---|
| Duolingo | `https://careers.duolingo.com/` 页面链接 Greenhouse API | 20 条边界采样均未通过具体岗位质量门禁 | 暂停，不重试 |
| Reddit | `https://www.redditinc.com/careers` 页面链接 `job-boards.greenhouse.io/reddit` | API 返回验证页 `verification_page_detected` | 暂停，不重试 |

两家均未写入有效岗位，未计入新增企业。未使用登录、验证码、代理或访问控制绕过。
