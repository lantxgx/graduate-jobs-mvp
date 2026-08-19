# 岗位字段与入库契约

## 活动岗位必须满足

`title`、`city`、`category`、`degree`、`job_nature`、`description` 或 `requirements`、`apply_url`、`source_url`、`content_hash` 均不能为空；`job_nature` 只能是 `全职` 或 `实习`。

任何一项缺失都进入 `job_quarantine`，不能用 AI 猜测补齐，也不能直接显示为活动岗位。

## 采集到公网的固定流水线

```text
公开招聘入口
  -> 具体岗位列表
  -> 具体岗位详情
  -> 原始证据/响应快照
  -> 字段归一化与质量门禁
  -> SQLite jobs.db
  -> scripts/export_github_pages.py
  -> docs/jobs.json
  -> git push
  -> GitHub Pages 自动部署
```

## 其他 AI 不得做的事

- 不得把招聘计划、宣讲会、人才项目当成岗位。
- 不得猜测详情 URL、调用隐藏接口、绕过登录/验证码/安全验证。
- 不得批量并发访问或使用代理池规避限制。
- 不得删除旧岗位、快照、失败记录或隔离记录。
- 不得提交 `.env`、API Key、`data/jobs.db`、简历和用户数据。

## 验收命令

```powershell
& .\.venv\Scripts\python.exe -m pytest -q
& .\.venv\Scripts\python.exe scripts/export_github_pages.py
```

导出后检查 `docs/jobs.json` 中每条记录的公司、城市、岗位、招聘类型、学历、描述和官方投递 URL；再打开本地页面检查检索和详情。

