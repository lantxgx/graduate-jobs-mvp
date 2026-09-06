# SRC-20260907-honycapital-feishu-campus

- company: 弘毅投资（Hony Capital）
- official_ownership_url: https://www.honycapital.com/
- source_url: https://honycapital.jobs.feishu.cn/campus
- checked_at: 2026-09-07
- state: skipped_adapter_mismatch

## Evidence

- 弘毅投资官网“联系我们”页面明确把“校园招聘”链接到该飞书门户。
- 一次有界公开采集未发现现有飞书适配器要求的具体 `/position/.../detail` 岗位链接。

## Decision

官方归属成立，但当前页面结构无法取得具体岗位详情。未猜测私有接口、未登录或绕过访问控制，未写入岗位；已移除临时配置，后续不重复请求，除非公开页面结构发生变化。
