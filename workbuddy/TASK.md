---
task_id: WB-AUDIT-001
status: ready
created_at: 2026-08-15
owner: WorkBuddy-HY3
reviewer: Codex
task_type: capability_audit
allow_external_access: false
allow_database_changes: false
allow_business_code_changes: false
---

# WorkBuddy 桌面端能力、Skill 和连接器审计

## 目标

在开始任何开发前，准确确认当前 WorkBuddy 桌面端能做什么、不能做什么、需要安装哪些 Skill/连接器，以及能达到 A0/A1/A2 哪种自动化等级。

这不是开发任务。禁止修改业务代码、数据库、配置和历史文档。

## 必须完整读取

按顺序完整读取：

1. `workbuddy/PROTOCOL.md`
2. `workbuddy/BASELINE.md`
3. `workbuddy/FEATURE_REQUIREMENTS.md`
4. `workbuddy/AUTOMATION.md`
5. `workbuddy/CAPABILITY_AUDIT_RESULT.md`

不要读取 `.env`、`data/jobs.db` 内容、历史 Harness 或其他无关文件。

## 允许修改

- `workbuddy/TASK.md`
- `workbuddy/CAPABILITY_AUDIT_RESULT.md`
- `workbuddy/RESULT.md`

禁止修改其他文件。

## 审计步骤

### 步骤 1：记录界面直接可见能力

在 `CAPABILITY_AUDIT_RESULT.md` 填写：WorkBuddy 版本、HY3 模型名称、界面上可见的 Skill、连接器、Agent/自动化/终端/浏览器入口。看不到就写“界面未发现”，不得猜测。

### 步骤 2：最小测试 CAP-01 文件读写

1. 读取本任务的 `task_id`；
2. 将 `TASK.md` 的状态从 `ready` 改为 `in_progress`；
3. 在结果表中记录成功证据。

如果连状态都不能修改，停止并写 `blocked`。

### 步骤 3：最小测试 CAP-02 终端

如果存在终端能力，只运行以下只读命令：

```powershell
Get-Location
Get-ChildItem workbuddy -File | Select-Object Name
node --version
& .\.venv\Scripts\python.exe --version
```

记录命令、退出码和版本。没有终端则标 `NEED_CONNECTOR`，不要假装执行。

### 步骤 4：检查但不使用其他能力

对 CAP-03 至 CAP-10，只检查界面或已安装工具列表。此任务禁止：

- 打开外部网站；
- 上传文件；
- 连接数据库；
- 控制本地服务；
- 安装 Skill 或连接器；
- 运行自动化脚本。

没有直接证据时写 `UNKNOWN` 或 `NEED_CONNECTOR`。

### 步骤 5：评估 FR-001 至 FR-020

逐项填写“可执行 / 部分可执行 / 不可执行”、所需 CAP、缺口和建议执行者。不得遗漏任何 FR。

### 步骤 6：给出安装建议

只建议安装，不实际安装。按优先级说明：

- Skill/连接器名称或搜索关键词；
- 解决哪个 CAP/FR；
- 是否必须；
- 安装后最小验证方法；
- 是否涉及账号、网络或敏感权限。

### 步骤 7：判断自动化等级

根据 `AUTOMATION.md` 判断当前是 A0、A1 还是 A2。没有 CLI/API/Automation 证据时不能判定 A2。

## 完成要求

1. `CAPABILITY_AUDIT_RESULT.md` 的 CAP-01 至 CAP-10 全部填写；
2. FR-001 至 FR-020 全部填写；
3. 安装建议和自动化等级填写；
4. `RESULT.md` 记录本次只修改了三个允许文件；
5. 未访问外部网站、未修改数据库、未读取密钥；
6. 完成后将本文件 `status` 改为 `done`；无法完成则改为 `blocked`。

不要开始执行 `workbuddy/tasks/WB-001_ADMIN_SOURCE_FILTERS.md`。它必须等 Codex 验收能力审计后再进入当前任务。

