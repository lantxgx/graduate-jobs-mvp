# SRC-20260906-zhihu-moka-campus

- company: 知乎
- source_id: zhihu-moka-campus
- official listing URL: https://app.mokahr.com/campus-recruitment/zhihu/68321
- ownership evidence: https://www.zhihu.com/careers
- adapter: `moka`
- state: verified_sample
- checked_at: 2026-09-06

## Evidence

知乎官网招聘页明确包含“校园招聘”链接，目标为上述 Moka 门户。校招页 HTTP 200，并公开返回岗位卡片/详情数据。

## Collection

首次采集限制为 10 条，`snapshot_complete=false`。实际结果：listed=10、accepted=10、created=10、updated=0、quarantined=0。失败或字段不完整的岗位进入隔离，不猜测字段。
