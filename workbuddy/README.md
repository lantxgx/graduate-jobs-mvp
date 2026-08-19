# WorkBuddy 桌面端共享执行入口

本目录用于把 WorkBuddy 免费 HY3 模型作为“本地执行工”，Codex 负责拆任务、风险控制和最终验收。

WorkBuddy 每次从以下文件开始：

1. `PROTOCOL.md`：长期执行规则；
2. `BASELINE.md`：产品、数据、安全、代码和测试基线；
3. `TASK.md`：当前唯一任务；
4. 任务明确指定的功能需求或审计文件；
5. `RESULT.md`：完成后填写的回执。

不要让 WorkBuddy 一次读取项目里的全部方案文档。需要的背景已经由 Codex压缩到任务文件中，可以减少上下文和误解。

完整功能边界见 `FEATURE_REQUIREMENTS.md`，桌面端自动化等级和限制见 `AUTOMATION.md`。排队任务保存在 `workbuddy/tasks/`，WorkBuddy 不得自行执行。

## 你每次怎么操作

1. 在 WorkBuddy 桌面端打开项目目录：

   `F:\牛投马面\V0.1\graduate-jobs-mvp`

2. 新建一个 WorkBuddy 对话，复制 `START_PROMPT.txt` 的全部内容发送。
3. WorkBuddy 完成后，确认 `workbuddy/RESULT.md` 已填写。
4. 回到 Codex，只需要说：

   `WorkBuddy 已完成，请验收 workbuddy/RESULT.md`

5. Codex 检查真实文件、测试和页面。通过后，Codex 会把下一条任务写入 `TASK.md`。

当前第一步不是开发，而是 `WB-AUDIT-001` 能力审计。WorkBuddy 需要先填写 `CAPABILITY_AUDIT_RESULT.md`，列出哪些能力原生可用、哪些需要 Skill/连接器。审计通过后，排队的 `WB-001_ADMIN_SOURCE_FILTERS` 才会进入当前任务。

## 状态约定

- `ready`：等待 WorkBuddy 执行；
- `in_progress`：WorkBuddy 正在执行；
- `done`：WorkBuddy 自认为完成，等待 Codex 验收；
- `blocked`：遇到任务范围内无法解决的问题；
- `accepted`：Codex 已验收通过，可以生成下一任务。

同一时间只能有一个 `ready` 或 `in_progress` 任务。不要同时开启多个 WorkBuddy 对话修改同一项目。

## 模型分工

WorkBuddy/HY3 适合：明确的前端修改、fixture 解析、字段映射、单元测试、文档同步和机械化排错。

Codex 保留：真实招聘网站首次探查、来源官方性判断、风控处理、数据库迁移、批量岗位修改、推荐策略和最终验收。
