# SRC-20260907-desaysv-feishu-campus

- company: 德赛西威
- source_url: https://yesv-desaysv.jobs.feishu.cn/index
- official_ownership_url: https://www.desaysv.com/
- checked_at: 2026-09-07
- state: skipped_missing_detail_fields

## Evidence

- 德赛西威官网直接链接到上述飞书招聘入口，页面无需登录即可访问。
- 一次有界采集发现具体岗位详情链接，但详情未通过现有字段质量门禁：`https://yesv-desaysv.jobs.feishu.cn/index/position/7681564518443174171/detail`。

## Decision

当前详情字段不完整，未猜测缺失字段、未写入岗位。按停止规则跳过，不重复请求；后续需有新的公开字段证据或专用适配器后再处理。
