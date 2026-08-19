# WorkBuddy 桌面端自动工作方案

## 1. 先说结论

只有桌面 GUI、没有 CLI/API/自动化连接器时，Codex 无法直接把任务推送到 WorkBuddy，也无法在它完成后自动唤醒下一轮模型。文件共享可以自动同步任务和结果，但“点击发送、开始新一轮推理”仍需要用户或桌面自动化工具触发。

因此分为三个自动化等级：

| 等级 | 使用条件 | 用户操作 | 推荐程度 |
|---|---|---|---|
| A0 手工触发 | 只有桌面聊天界面 | 每个任务复制一次启动提示 | 最稳定，立即可用 |
| A1 单会话连续执行 | WorkBuddy 能读文件、改文件、运行终端，并支持 Agent/连续模式 | 每个任务开始时发送一句“读取当前任务并执行” | 推荐先验证 |
| A2 桌面自动化触发 | 有 WorkBuddy Automation、Power Automate Desktop 或可靠 UI 自动化 | 监控任务状态并自动聚焦窗口、粘贴和发送 | 验证 UI 后再做 |

不要让 HY3 自己写一个无限循环等待新任务。模型完成一次回复后通常不会因为文件变化自动醒来；死循环还可能占用终端和误触发重复执行。

## 2. 文件状态机

共享状态只看 `workbuddy/TASK.md`：

```text
ready
  ↓ WorkBuddy 开始
in_progress
  ↓ 成功                       ↓ 无法继续
done                         blocked
  ↓ Codex 验收
accepted / changes_requested
  ↓ Codex 写入下一任务
ready
```

规则：

- 同时只有一个当前任务；
- WorkBuddy 只能写 `in_progress/done/blocked`；
- Codex 只能在验收后写 `accepted/changes_requested/ready`；
- `RESULT.md` 的 `task_id` 必须与 `TASK.md` 相同；
- 任务编号不复用；
- 被替换的任务移入 `workbuddy/tasks/` 保留回溯。

## 3. A0：现在就能用的方式

每个任务：

1. 用户确认 `TASK.md` 状态为 `ready`；
2. 在 WorkBuddy 新建或继续项目对话；
3. 发送 `START_PROMPT.txt`；
4. WorkBuddy 执行并写 `RESULT.md`；
5. 用户回 Codex 发送：`WorkBuddy 已完成，请验收`；
6. Codex 验证后更新下一任务。

这个模式每轮只需要用户两次操作，不需要额外软件。

## 4. A1：WorkBuddy Agent/连续模式

只有在能力审计证明 WorkBuddy 能够：

- 读取共享目录；
- 修改指定文件；
- 运行 PowerShell；
- 在长任务中不中断；

才使用 A1。

每个任务只发送下面一句：

```text
读取 workbuddy/PROTOCOL.md、BASELINE.md 和当前 TASK.md，执行到 done 或 blocked，填写 RESULT.md；不要等待逐步确认。
```

即使使用 A1，也不要让它自动执行下一条 `ready` 任务。Codex 必须先验收上一条结果，避免错误累积。

## 5. A2：真正自动点击桌面端

A2 需要以下任一能力：

- WorkBuddy 官方 Automation/任务队列；
- WorkBuddy CLI/API；
- Power Automate Desktop；
- AutoHotkey 或其他桌面 UI 自动化。

推荐触发逻辑：

```text
每 60 秒只读检查 TASK.md
→ status != ready：不动作
→ status == ready 且 task_id 未发送过：
   聚焦 WorkBuddy 窗口
   新建项目对话或定位固定对话
   粘贴固定启动提示
   点击发送
   记录已发送 task_id
→ 等 WorkBuddy 把状态改为 done/blocked
→ 给用户桌面通知
→ 不自动生成下一任务
```

必须具备的防重复字段：

```text
last_dispatched_task_id
last_dispatched_at
workbuddy_window_title
dispatch_status
```

在没有确认 WorkBuddy 窗口标题、输入框定位方式、发送按钮行为和完成信号前，不创建 UI 自动点击脚本。盲目坐标点击可能把任务发送到错误窗口或聊天。

## 6. WorkBuddy 没有网页抓取能力时怎么分工

WorkBuddy 不负责真实网页访问。流程改为：

```text
Codex/人工浏览器确认官方入口和公开内容
→ 保存脱敏 fixture
→ TASK.md 只引用 fixture 和确定字段
→ WorkBuddy 编写 adapter、normalize、测试
→ Codex 审查代码
→ Codex 执行最多 20 条真实样本
→ WorkBuddy 处理后续纯本地 UI/测试/文档
```

这样 WorkBuddy 即使没有浏览器，也能承担大部分机械开发，同时不会误爬网站。

## 7. Skill/连接器安装优先级

建议按顺序询问 WorkBuddy 是否支持：

1. Workspace/Filesystem；
2. Terminal/PowerShell；
3. Diff/Git；
4. Local Browser/Playwright；
5. SQLite；
6. PDF/DOCX；
7. Spreadsheet；
8. Scheduler/Automation；
9. External Browser Network/DevTools。

前 3 项足以执行大量代码任务。没有第 4、5 项时仍可通过单元测试和 fixture 工作。第 9 项风险最高，安装后也必须遵守单来源、低频和停止信号。

## 8. 成本控制

- 单任务只给 1-4 个允许修改文件；
- 每个任务只解决一个可验收行为；
- 任务中直接给出接口、字段、示例和命令；
- WorkBuddy 不重复解释方案，只写回执；
- Codex 只读取 diff、RESULT 和失败测试；
- 同一失败最多让 HY3 修两轮，第三轮交回 Codex；
- 不把完整历史对话发送给 HY3。

