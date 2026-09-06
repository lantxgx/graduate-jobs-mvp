# SRC-20260907-seer-feishu-campus

- company: 仙工智能
- source_url: https://seer-group.jobs.feishu.cn/index
- official_ownership_url: https://www.seer-group.com/
- checked_at: 2026-09-07
- state: skipped_adapter_mismatch

## Evidence

- 仙工智能官网直接链接到上述飞书招聘入口，页面无需登录即可访问。
- 一次有界采集未发现可验证的具体 `/position/.../detail` 岗位链接。

## Decision

现有飞书适配器无法取得具体岗位列表，未猜测私有接口、未写入岗位。按停止规则跳过，不重复请求；除非公开页面结构发生变化，否则不再尝试。
