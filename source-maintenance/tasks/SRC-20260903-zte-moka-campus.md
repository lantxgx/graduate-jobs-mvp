# SRC-20260903-zte-moka-campus

- company: 中兴通讯
- source_id: zte-moka-campus
- official listing URL: https://app.mokahr.com/campus-recruitment/zte/46903
- ATS: Moka
- checked_at: 2026-09-03T17:14:44+08:00 (+08:00)

## Result

- active jobs after refresh: 24
- newly accepted by this run: 14
- worker error: none
- snapshot completeness: false (bounded source configuration)
- roster status: 部分失败

## Follow-up refresh

- 2026-09-03 14:17 +08:00：扩大有界详情抓取至 20 条，发现 19 条公开岗位；新增 14 条、更新 5 条。
- 仍有 3 条历史活动记录缺少官方任职要求，未伪造字段，也未在不完整快照下停用旧记录。
- 当前来源保留观察状态，待这 3 条记录获得官方详情或完整快照后再申请正式集成。

## Command

```powershell
.\.venv\Scripts\python.exe -m crawler.worker --source zte-moka-campus
```

The source remains bounded. No claim of exhaustive public pagination is made until a complete traversal can be demonstrated.
