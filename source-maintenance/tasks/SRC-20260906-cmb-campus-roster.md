# SRC-20260906-cmb-campus-roster

- company: 招商银行
- source_id: cmb-campus-roster
- official listing URL: https://career.cmbchina.com/positionlist
- adapter: `cmb`
- state: integrated_sample
- checked_at: 2026-09-06
- scope: 招商银行官网公开校园招聘实习岗位

## Evidence

- 官网列表页公开展示具体岗位：`https://career.cmbchina.com/positionlist`
- 列表接口：`POST https://career.cmbchina.com/api/campusRecruitmentWebsite/job/getList`
- 详情接口：`GET https://career.cmbchina.com/api/campusRecruitmentWebsite/job/getDetail?publishId=<publishGID>`
- 招聘类型：`DF94FD6D-26D3-4A19-9E69-577C4BA1DE82`
- 已验证详情 ID：`131059E1-BBCC-4530-A573-7F91B26EB45F`

## Collection

- 首次采集上限：10 条，按交接要求保持 bounded sample。
- 实际列表：10 条；详情合格：10 条；新增：10 条；更新：0 条；隔离：0 条。
- `snapshot_complete=false`：本次不是完整分页快照，不能据此下架历史岗位。
- 来源验证脚本已通过：`official_status=confirmed`、`integration_status=integrated`、`active_jobs=10`、`latest_crawl_success=10`；岗位契约门禁通过。

## Next action

已运行单来源 worker、导出脚本和来源验证。若后续接口出现 403/429，立即记录并暂停，不重试或绕过访问控制。
