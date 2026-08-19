---
task_id: WB-001
status: queued
created_at: 2026-08-15
owner: WorkBuddy-HY3
reviewer: Codex
allow_external_access: false
allow_database_changes: false
depends_on: WB-AUDIT-001
---

# 数据管理页增加本地来源筛选

本任务暂不执行。只有能力审计证明 CAP-01 文件读写、CAP-02 终端可用后，Codex 才会把它复制到当前 `TASK.md` 并改为 `ready`。

## 目标

让 `/admin/sources` 在不访问招聘官网、不触发采集的情况下，按企业关键词、招聘系统、官方状态和接入状态筛选现有来源。

## 允许修改

- `static/admin-sources.html`
- `static/admin-sources.js`
- `static/styles.css`
- `tests/test_pages.py`（确实需要时）
- `workbuddy/TASK.md`
- `workbuddy/RESULT.md`

## 功能要求

1. 来源表格上方新增企业关键词、招聘系统、官方状态、接入状态四个筛选字段，以及“筛选”“重置”按钮。
2. 招聘系统至少包含全部、feishu、beisen、moka、self_hosted、custom。
3. 官方状态至少包含全部、confirmed、candidate、unverified、excluded，并显示中文标签。
4. 接入状态至少包含全部、integrated、analyzing、not_integrated、excluded，并显示中文标签。
5. 点击筛选后使用 `URLSearchParams` 请求 `/api/company-sources`，传递非空的 `company`、`ats_type`、`official_status`、`integration_status` 和 `limit=200`。
6. 企业输入框按 Enter 可以筛选。
7. 重置清空筛选并恢复全部来源。
8. `sourceSummary` 保留总体统计并补充“当前显示 N 条”。
9. 请求失败显示中文错误，不清空现有表格。
10. 不调用任何 `/api/crawl/` 接口，不增加定时器，不改其他页面。
11. 修改脚本后更新 HTML 中静态资源版本参数。

## 验收

```powershell
node --check static/admin-sources.js
& .\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py' -q
```

完成后必须提供：修改前/后行为、修改文件、实际命令和退出码、测试数量、无外部访问和无数据库修改声明。

