# Graduate Radar / 应届生招聘雷达 V0.2

使用方式见 [USAGE_GUIDE.md](USAGE_GUIDE.md)。Luna 可直接执行的岗位采集、字段标准化和自动更新规格见 [LUNA_EXECUTABLE_JOB_INGESTION_PLAN.md](LUNA_EXECUTABLE_JOB_INGESTION_PLAN.md)。

使用 WorkBuddy 桌面端免费模型分担本地开发时，从 [workbuddy/README.md](workbuddy/README.md) 开始；当前唯一任务在 `workbuddy/TASK.md`。

本地代码更新后可执行 `.\restart_server.ps1` 重启服务；脚本只检查并重启本项目在 `127.0.0.1:8000` 的监听进程，然后用 `/health` 做有界验证。

## GitHub Pages 公开预览

`docs/` 是只读的 GitHub Pages 演示版，保留岗位搜索、筛选、详情和官方投递链接，不包含采集、简历 AI、收藏写入或数据管理操作。更新本地岗位数据后执行：

```powershell
& .\.venv\Scripts\python.exe scripts/export_github_pages.py
```

提交更新后的 `docs/jobs.json` 后，`.github/workflows/pages.yml` 会自动发布 GitHub Pages。SQLite 数据库和 `.env` 仍保持在 Git 之外。

一个面向应届生的公开招聘官网聚合 Web MVP。

它做四件事：

1. 打开企业公开校园招聘官网；
2. 监听页面加载的 XHR/fetch JSON；
3. 自动识别职位对象，并统一成「公司 / 职位 / 城市 / 职能 / 职位性质 / 学历 / 要求 / 官方投递链接」；
4. 在 Web 页面中搜索和筛选。

> 这是一个“发现型采集器”MVP。第一次接入某个新官网时，先通过浏览器发现真实的公开 JSON 接口；
> 稳定运行后，建议把高频来源改成 source-specific adapter，直接请求该公开接口，速度更快、资源更省。

## 已放入的初始来源

- 远景科技集团校园招聘：
  `https://envision-career.com/campus-recruitment/envisiongroup/43123/#/jobs`
- 小米校园招聘：
  `https://hr.xiaomi.com/campus/recruitment`
- 叠纸游戏校园招聘：
  `https://career.papegames.com/campus/position/list`
- OPPO校园招聘：
  `https://careers.oppo.com/university/oppo/campus/post`
- MiniMax 校园招聘（飞书公开入口）：
  `https://vrfi1sk8a0.jobs.feishu.cn/s/i6nd8qwp`

来源配置在 `config/sources.json`，可以继续增加公司。

## 本地运行

建议 Python 3.11 / 3.12。

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

先抓取一次：

```bash
python -m crawler.runner
```

也可以只抓一个来源：

```bash
python -m crawler.runner --source envision-campus
```

将配置文件中的来源同步到“数据管理”注册表（只登记，不确认官方性、不抓取、不写入岗位）：

```bash
python -m crawler.source_registry --source-file config/sources.json
```

登记后的来源默认为 `candidate / analyzing`，必须完成官方归属、公开访问和最多 20 条小样本验收后，人工改为 `confirmed / integrated`，才允许调度器自动更新。

受控单来源 worker：

```bash
python -m crawler.worker --source envision-campus
```

启动 Web：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

打开：

```text
http://localhost:8000
```

## API

- `GET /api/jobs`：职位查询
- `GET /api/jobs?offset=0&limit=100`：分页职位查询，返回 `items/total/offset/limit`；不带 `offset` 保持旧数组响应兼容
- `GET /api/facets`：筛选项 / 统计
- `GET /api/job-quality`：活动岗位必需字段、隔离记录和缺失字段审计
- `GET /api/sources`：采集来源
- `GET /api/companies`：企业数据源注册表中的企业列表
- `GET /api/company-sources`：企业招聘入口列表，可按 ATS、官方性、访问和接入状态筛选
- `GET /api/company-source-stats`：企业与招聘入口状态统计
- `POST /api/resume/preview`：当前会话解析 PDF/DOCX 简历并返回待确认画像，不保存原文件
- `GET /api/recommendations`：按画像返回四类可解释推荐池
- `POST /api/jobs/{job_id}/action`：收藏、忽略或标记已投递
- `GET /profile`：用户能力证据、求职意愿和简历处理页
- `GET /admin/sources`：企业入口、质量、队列和采集运行管理页
- `GET /api/job-actions?action=favorite|ignore|applied`：读取用户反馈状态，网页工作台据此恢复按钮和筛选视图
- `GET /api/profile`、`PUT /api/profile`、`DELETE /api/profile`：结构化能力画像与求职意愿
- `POST /api/resume/preview`、`POST /api/resume/analyze`：当前会话简历预览和可选 AI 结构化分析
- `GET /api/ingestion-queue`：按质量和优先级查看待小样本接入的企业入口
- `GET /api/crawl-runs`：采集运行记录
- `GET /api/source-snapshots`：岗位源快照、异常骤降保护和保护原因
- `GET /api/job-updates?since=<ISO timestamp>&limit=100`：读取新增或详情发生变化的活动岗位，只读，不触发采集
- `POST /api/crawl/{source_id}`：将单来源采集放入后台任务，受冷却和来源锁保护
- `GET /health`：健康检查

推荐接口返回 `match_dimensions`，分别说明基本资格、能力匹配、求职意愿、企业偏好、转型距离和证据置信度，并返回 `recall_channels` 说明岗位由关键词、岗位族、技能证据、目标企业或相邻岗位通道召回。`ignore` 只影响默认推荐，不会从 `/api/jobs` 的完整检索中删除岗位。

示例：

```text
/api/jobs?keyword=算法&city=北京&company=小米集团
```

## 新增一家企业

编辑 `config/sources.json`：

```json
{
  "id": "company-campus",
  "company": "某公司",
  "name": "某公司校园招聘",
  "url": "https://example.com/campus/jobs",
  "mode": "browser_json",
  "campus_only": true,
  "enabled": true
}
```

然后运行：

```bash
python -m crawler.runner --source company-campus
```

采集结果会输出 `json_endpoints_seen`，它对后续制作稳定的专用 adapter 很重要。

## 数据库

MVP 使用 SQLite：`data/jobs.db`。

核心字段：

- `company`
- `title`
- `city`
- `job_nature`
- `category`
- `degree`
- `graduate_year`
- `requirements`
- `description`
- `apply_url`
- `source_url`
- `published_at`
- `first_seen_at`
- `last_seen_at`
- `status`

正式上线时可以迁移到 PostgreSQL。

## 推荐的下一阶段

### 1. 每家重点公司建立专用 Adapter

浏览器发现到公开 JSON endpoint 后：

```text
Playwright Discovery
        ↓
记录公开职位 API
        ↓
专用 HTTP Adapter
        ↓
更快、更稳定、更节省资源
```

### 2. 加入字段标准化

例如城市：

```text
北京市 / 北京市海淀区 / Beijing
               ↓
              北京
```

职位类别：

```text
后端开发 / Java / Go / 服务端
               ↓
            软件研发
```

### 3. 加“应届条件解析”

从岗位描述中提取：

- 2027 届 / 2026 届
- 本科 / 硕士 / 博士
- 专业要求
- 技能关键词
- 语言要求
- 实习 / 正式校招
- 截止日期

这一层可以先规则解析，后续再接 LLM 做结构化抽取。

### 4. 定时任务

生产环境不要让 API 请求同步执行采集。
把采集器放到 Worker / Cron 中，例如每 4~12 小时更新一次，并为每个来源设置合理频率。

## 合规边界

- 只采集公开、无需登录即可浏览的招聘信息；
- 尊重网站服务条款、robots 规则及合理访问频率；
- 不绕过验证码、登录、访问控制或反自动化保护；
- Web 中保留来源链接和官方投递链接；
- 对职位状态、截止日期等重要信息以企业官网为准。
- 采集器按来源串行运行并默认设置 3600 秒冷却；通用发现器遇到 403、429、验证码或安全验证立即停止，不重试、不绕过；只有通过具体岗位字段质量门槛的结果才能写入岗位表。

## GitHub

当前目录可直接初始化：

```bash
git init
git add .
git commit -m "feat: graduate jobs radar MVP"
```

之后新建 GitHub repository 并 push 即可。
