# SRC-20260907-agibot-feishu-campus

- company: 智元机器人（AGIBOT Innovation）
- source_id: agibot-feishu-campus
- official listing URL: https://agirobot.jobs.feishu.cn/campusrecruitment
- ownership evidence: https://www.agibot.com.cn/
- adapter: `feishu_jobs_browser`
- state: verified_sample
- checked_at: 2026-09-07

## Evidence

智元机器人中文官网公开“人才招聘”入口，并明确链接“校园招聘”到上述飞书门户；无需登录、验证码或访问控制绕过。门户公开展示具体职位详情，详情包含职位描述、职位要求、城市、招聘性质和投递链接。

## Collection

先以 2 条公开详情做适配验证：列表和详情均可访问，2/2 通过字段门禁。正式 worker 首次采集上限为 5 条，实际 listed=5、accepted=5、created=5、quarantined=0；`snapshot_complete=false`，不以样本宣称全量覆盖。

## Skip evidence from the same easy-source sweep

本轮没有继续尝试已发现但不合格的其他飞书入口：01.AI 无具体岗位链接，Babycare 详情字段门禁失败；趣维科技无具体岗位链接，沐瞳科技、深势科技详情字段门禁失败，店匠科技无具体岗位链接。它们未写入配置，也不重复请求。

## Next action

运行单来源 worker、来源验证和导出；若出现 403/429、验证码或详情字段不完整，暂停该来源并保留失败证据。
