# Luna 可直接执行：校招岗位收集与自动更新 Runbook

> 目标：把企业官网公开的具体岗位，可靠地同步到“找岗位”。活动岗位的招聘类型只允许“全职”和“实习”。

## 1. 方案结论

采用“来源注册表 + 来源适配器 + 统一标准化 + 质量闸门 + 单来源低频调度”的组合，不采用一个万能爬虫。

可复用的开源思路：

- Scrapy：请求、限速、重试、Item/Pipeline 思路；当前项目已有单来源 Worker，因此不整体迁移。
- Playwright：仅用于必须执行 JS 的公开招聘页面，并只解析渲染后可见内容。
- Greenhouse/Lever 等公开 ATS feed：优先使用企业明确归属的公开岗位 feed。
- changedetection.io：借鉴列表快照/hash 变化检测，变化后才抓详情。
- Crawl4AI：只作为自建站 HTML 提取的可选参考，不绕过验证码、登录墙或访问控制。
- JobSpy：仅用于发现企业/官网线索，不作为官方岗位主数据源。

## 2. 统一岗位记录

每条进入活动岗位的记录至少包含：

```json
{
  "company": "公司标准名",
  "city": "上海 / 北京",
  "category": "软件研发",
  "title": "Backend Engineering Intern",
  "job_nature": "实习",
  "degree": "本科及以上",
  "description": "官网岗位描述",
  "requirements": "官网任职要求",
  "apply_url": "具体岗位详情或投递链接",
  "source_url": "官方招聘入口",
  "source_job_id": "官方岗位 ID",
  "published_at": "可选",
  "content_hash": "规范化内容哈希"
}
```

硬规则：

1. `job_nature` 只能是 `全职` 或 `实习`；未知、兼职、外包、劳务、社会招聘不进入活动岗位。
2. `apply_url` 必须是页面或公开 feed 明确给出的具体岗位 URL；禁止猜 URL。
3. 必须有具体岗位标题、城市、招聘类型，以及描述或要求中的至少一项。
4. 招聘计划、项目介绍、导航卡片、公司介绍不是岗位。
5. 字段不完整的记录进入 `job_quarantine`，不污染 `jobs`。

## 3. 企业接入的 8 个执行单元

每次只处理一个 `source-key`，按顺序执行：

### S1：确认官方入口

把来源先登记为 `candidate/analyzing`，记录企业官网到招聘入口的证据、最终域名、ATS 类型和岗位详情 URL 样本。此阶段不写岗位。

### S2：建立离线 fixture

在 `tests/fixtures/<source-key>/` 保存脱敏的列表和详情样本。测试不得访问网络。

### S3：选择适配器

优先级：已确认的公开 ATS feed > 企业专用 JSON/API > 服务端 HTML > 可见 HTML 卡片 + Playwright。只有公开页面已经出现的链接才可使用。

当前适配器：`greenhouse`、`lever`、`custom_html`，以及已有企业专用适配器。

### S4：通过标准化测试

至少测试城市、岗位标题、职能、学历、描述、要求、详情 URL、全职、实习、未知招聘类型拒绝、导航卡拒绝、缺 URL 拒绝。

### S5：一次受控真实小样本

最多 20 条，串行、低频、只读。遇到 403、429、验证码、安全验证、登录墙、详情 URL 不明确，立即停止并暂停来源。

### S6：写库并验证前端

只通过现有 runner/upsert 写入；验证 `/api/jobs` 和“找岗位”页面能按公司、城市、职能、招聘类型、学历筛选，并能打开官方详情链接。

### S7：准入状态

S1-S6 全部通过后才允许 `confirmed/integrated`；否则保持 `candidate/analyzing/paused`。

### S8：记录 Harness

记录请求次数、岗位发现/接收/隔离数量、失败原因、保护动作、测试结果和下一步。禁止删除历史岗位、失败记录、隔离记录或用户数据。

## 4. 自动更新策略

- 默认同一来源间隔 12 小时；有明确列表变化时才缩短到 6 小时。
- 单来源串行、source lock、最多 20 条；不使用代理池、指纹伪装或验证码绕过。
- 优先使用 ETag/Last-Modified 和列表 hash；列表没有变化时不抓详情。
- 只有新岗位、列表中发生变化的岗位或详情超过 7 天未检查时才请求详情。
- 单次空快照或岗位数下降超过 50% 时启用快照保护，不下线已有岗位。
- 连续 3 次完整健康快照缺失才标记岗位 inactive；下一次恢复则恢复。
- 普通失败使用 1/3/12/24 小时退避；403/429/验证/登录墙不自动重试，等待人工复核。
- 保护性停止必须把 `paused_reason` 写入来源并清空 `next_run_at`；人工确认后才恢复调度。

## 5. Luna 执行命令

```powershell
Set-Location 'F:\牛投马面\V0.1\graduate-jobs-mvp'

& .\.venv\Scripts\python.exe -m compileall -q app crawler tests
& .\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py' -q
node --check static/app.js
Invoke-WebRequest http://127.0.0.1:8000/health

# 每次只替换一个来源；没有明确详情 URL 时只做离线分析，不执行真实采集
& .\.venv\Scripts\python.exe -m crawler.worker --source <source-key>

Invoke-WebRequest 'http://127.0.0.1:8000/api/jobs?limit=20'
Invoke-WebRequest 'http://127.0.0.1:8000/api/job-quality'
Invoke-WebRequest 'http://127.0.0.1:8000/api/job-quarantine'
```

已有有效岗位但数据管理仍显示为 `candidate/analyzing` 时，先执行一次显式白名单对账：

```powershell
& .\.venv\Scripts\python.exe -m crawler.source_registry --promote-verified
```

该命令只处理明确登记的已验证适配器，且要求来源存在活动岗位、没有暂停原因；不会创建、删除或重新抓取岗位，也不会升级普通候选来源。

企业名称发生变化时，先使用明确别名白名单做主数据对账，再查看企业目录；禁止通过模糊字符串匹配合并未知企业。

## 9. 本地自动更新进程

启动低频调度器：

```powershell
.\start_scheduler.ps1
```

停止低频调度器：

```powershell
.\stop_scheduler.ps1
```

脚本只操作自身 PID 文件中、且命令行明确包含 `crawler.scheduler --loop` 的进程；调度器每轮只选择一个到期来源，来源间隔、source lock、失败退避和保护性暂停仍由 Python 调度器负责。日志写入 `scheduler.stdout.log` 和 `scheduler.stderr.log`。

对于历史上已经完成过全量盘点的来源，后续自动更新必须切换为有界增量列表；不得因为 `snapshot_complete` 旧配置而重复全量抓取。全量盘点只能作为单独、低频、可审计的人工执行单元。

## 6. 交付验收

- 活动岗位必填字段缺失率为 0。
- 活动岗位招聘类型集合严格等于 `{全职, 实习}`。
- 计划/活动/导航卡片和无具体详情链接记录进入隔离，不进入“找岗位”。
- 新岗位无需修改前端静态卡片即可出现。
- 普通检索保留完整岗位集合；AI 只做排序、解释和推荐，不删除岗位。
- 失败来源不覆盖已有有效快照，每次真实运行都有 Harness 记录。

## 7. 当前执行顺序

1. 已完成并验证 `custom_html` 可见岗位卡片适配器。
2. 下一步选一个已确认官方归属且有具体详情 URL 的来源，先做 S1-S4。
3. 仅 S1-S4 全通过后，最多做一次 20 条真实样本。
4. 通过后写入岗位库，重启本地服务，检查“找岗位”和质量接口。
5. 最后再接入调度，不在服务启动时自动触发采集。

已探查但暂缓的来源必须保留原因，例如 `concrete_detail_url_unresolved`；即使页面能显示大量岗位，只要无法给出可审计的具体详情/投递链接，也不能进入活动岗位。

## 8. 已有来源状态对账

如果数据库已有通过质量闸门的岗位，但数据管理仍显示来源为 `candidate/analyzing`，先执行一次显式白名单对账：

```powershell
& .\.venv\Scripts\python.exe -m crawler.source_registry --promote-verified
```

该命令只处理代码中明确列出的已验证适配器，且要求来源存在至少一条活动岗位、没有暂停原因；不会创建、删除或重新抓取岗位，也不会升级普通候选来源。
