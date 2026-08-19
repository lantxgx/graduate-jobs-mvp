# 校招岗位动态采集与自动更新方案

更新时间：2026-08-15

## 1. 当前结论

当前系统已经具备企业注册表、来源表、单来源 Worker、SQLite 来源锁、冷却保护、岗位质量门槛和前端岗位检索，不应更换整套技术栈。

当前缺口是：企业入口发现之后，没有足够多的 ATS 适配器把“招聘官网”转换成“具体岗位列表和岗位详情”。建议增加以下流水线：

```text
企业发现
→ 官方招聘入口验证
→ ATS 类型识别
→ 岗位列表增量获取
→ 新增/变化岗位详情获取
→ 标准化与质量校验
→ 快照差异计算
→ 写入岗位库
→ 前端展示
```

## 2. 推荐技术方案

### 2.1 来源层

`career_sources` 为每个招聘入口继续保存：

- 企业 ID、入口 URL、最终 URL、官方证据 URL；
- ATS 类型：`feishu`、`beisen`、`moka`、`workday`、`greenhouse`、`lever`、`custom`；
- 官方状态、访问状态、接入状态；
- 更新时间、最低更新间隔、连续失败次数、暂停原因；
- 适配器名称和非敏感配置，例如租户标识、列表路径、校招筛选参数。

入口发现只更新来源表，不直接生成岗位。

### 2.2 适配器层

每种 ATS 实现统一接口：

```python
class JobSourceAdapter:
    async def discover(self, source) -> SourceEvidence: ...
    async def fetch_listing(self, source, cursor=None) -> ListingPage: ...
    async def fetch_detail(self, source, item) -> RawJob: ...
    def normalize(self, raw_job) -> NormalizedJob: ...
```

获取顺序：

1. 优先调用招聘页面公开使用的 JSON 接口；
2. 其次解析服务端 HTML；
3. 只有公开页面必须执行 JavaScript 时才使用 Playwright；
4. 403、429、验证码、安全验证或登录墙立即停止并暂停来源；
5. 不使用代理轮换、指纹伪装或验证码绕过。

首批适配器顺序：

1. 飞书招聘；
2. 北森；
3. Moka；
4. Greenhouse、Lever、Ashby、Workday；
5. 企业自建页面。

### 2.3 原始证据与标准化

每次运行先保存来源级快照元数据；原始岗位需要保留可审计证据：

- 来源 ID；
- 来源岗位 ID；
- 列表页和详情页 URL；
- 获取时间；
- 原始内容哈希；
- 必要的原始 JSON/HTML 片段或快照引用。

标准岗位字段：

```text
company
title
city
job_nature
category
job_family
degree
graduate_year
description
requirements
published_at
apply_url
source_url
source_job_id
first_seen_at
last_seen_at
status
```

规则解析优先。Qwen 只用于岗位族、学历、技能、描述/要求拆分等结构化补充，必须逐条或小批量调用，不能生成原文中不存在的地点、学历或岗位要求。

### 2.4 去重与变化检测

岗位主键优先级：

```text
source_id + source_job_id
→ 规范化详情 URL
→ company + title + city + job_nature 的稳定指纹
```

每次采集计算：

- `new`：新岗位 ID，获取详情并写入；
- `changed`：内容哈希变化，重新获取详情并保留更新时间；
- `unchanged`：只更新 `last_seen_at`，不重复调用模型；
- `missing`：本次完整快照未出现，先记录缺失；
- `inactive`：连续 3 次完整健康快照缺失后才下线。

空快照、岗位数突然下降超过 50%、详情字段大面积缺失时触发快照保护，不覆盖现有有效岗位。

### 2.5 独立调度器

调度器必须独立于 FastAPI 进程运行，避免 Web 服务重启或多进程导致重复采集。

推荐新增：

```text
crawler/scheduler.py
crawler/adapters/base.py
crawler/adapters/feishu.py
crawler/adapters/beisen.py
crawler/adapters/moka.py
```

调度策略：

| 来源状态 | 建议间隔 |
|---|---:|
| 招聘旺季且近期有变化 | 6 小时 |
| 正常但近期无变化 | 12～24 小时 |
| 连续失败 | 1、3、12、24 小时退避 |
| 403/429/验证码/登录墙 | 自动暂停，人工复核 |
| 未通过小样本验收 | 禁止自动调度 |

每次只运行一个来源；设置少量随机抖动，使用 ETag、Last-Modified 和内容哈希减少无效请求。

## 3. 前端同步方式

“找岗位”不直接读取企业入口作为岗位，而是读取已通过质量门槛的 `jobs`。

企业目录应显示：

- 企业名称；
- 招聘官网；
- 当前活动岗位数；
- 最近成功更新时间；
- 接入状态；
- 暂无岗位、正在接入、访问受限等明确状态。

岗位接口继续分页查询活动岗位。新岗位成功写入后即可自动出现在前端，无需修改静态页面。

建议增加：

```text
GET /api/companies/{id}/jobs
GET /api/companies/{id}/collection-status
GET /api/jobs/changes?since=<timestamp>
```

## 4. 开源项目调研与取舍

### 推荐借鉴或局部采用

1. [Scrapy](https://github.com/scrapy/scrapy)
   - BSD-3-Clause，成熟 Python 采集框架；
   - 适合请求调度、重试策略、中间件、Item Pipeline；
   - 可用于后续规模扩大，但当前 MVP 不必立即迁移已有 Worker。

2. [Crawl4AI](https://github.com/unclecode/crawl4ai)
   - Apache-2.0，适合动态页面和结构化抽取；
   - 适合作为企业自建招聘页的低优先级回退方案；
   - 不应替代 ATS JSON 适配器，也不能替代质量门槛。

3. [changedetection.io](https://github.com/dgtlmoon/changedetection.io)
   - Apache-2.0，适合监控页面变化并通过 webhook 通知；
   - 可用于低频判断“入口是否变化”，减少无变化页面的详情访问；
   - 它不是岗位解析器，首版可先用现有内容哈希实现。

4. [ATS Job Scraper](https://github.com/YvetteZheng0812/ats-job-scraper)
   - MIT，展示了 Ashby、Greenhouse、Lever、SmartRecruiters、Workable、Rippling、Workday 的公开 ATS 接口适配思路；
   - 适合借鉴统一适配器、公司发现、列表获取和导出结构；
   - 项目规模较小，且不支持飞书、北森、Moka，不能直接作为国内校招核心依赖。

### 可作为补充，不适合作为主数据源

5. [JobSpy](https://github.com/speedyapply/JobSpy)
   - MIT，主要抓 LinkedIn、Indeed、Glassdoor、Google、ZipRecruiter 等第三方招聘平台；
   - 不擅长企业官方校招 ATS，且其代理绕过能力不符合本项目保守访问策略；
   - 只能作为岗位发现线索，不能作为官方投递数据源。

6. [Campus Jobs Scraper](https://github.com/hunhunzhang/Campus-Jobs-Scraper)
   - 包含米哈游、字节、腾讯、美团的企业级脚本，可参考接口发现和字段清洗思路；
   - 当前仓库未声明许可证，不应直接复制代码进入产品；
   - 企业专用脚本维护成本高，适合作为适配器设计参考。

7. [SimplifyJobs/New-Grad-Positions](https://github.com/SimplifyJobs/New-Grad-Positions)
   - 活跃的新毕业生岗位社区列表；
   - 适合发现企业和入口，主要覆盖海外技术岗位；
   - 不是企业官方完整快照，不能用于岗位失效判断。

## 5. 最合适的落地组合

推荐组合：

```text
现有 FastAPI + SQLite/PostgreSQL
+ 现有单来源 Worker 和来源锁
+ 自研飞书/北森/Moka ATS 适配器
+ ATS Job Scraper 的海外 ATS 设计模式
+ Playwright/Crawl4AI 作为自建动态页面回退
+ 内容哈希与快照保护
+ 独立 scheduler 低频串行更新
```

当前不建议：

- 用 JobSpy 替换官方企业来源；
- 全面迁移 Scrapy 后才开始接入企业；
- 部署 changedetection.io、消息队列、PostgreSQL 后才验证第一个适配器；
- 使用 Qwen 直接浏览和抓取整站；
- 自动绕过访问限制。

## 6. 分阶段实施

### D-007：增量更新内核

- 增加来源调度字段、运行状态和连续失败次数；
- 实现 `new/changed/unchanged/missing/inactive` 差异计算；
- 增加连续 3 次缺失才下线规则；
- 为所有逻辑建立离线 fixture 测试。

验收：空快照和骤降不会清空岗位；未变化岗位不请求详情、不调用模型。

### D-008：飞书适配器

- 选 1 家官方公开、无需登录的企业；
- 获取最多 20 条校招岗位及详情；
- 字段完整率 100%，导航卡片误入为 0；
- 通过后扩展到 3 家使用同结构的企业。

### D-009：北森适配器

- 使用本地脱敏 fixture 先完成解析；
- 单来源、单次、小样本真实验证；
- 403、429 或安全验证立即停止。

### D-010：Moka 与自建页面

- Moka 继续使用确定性接口适配；
- 自建页面使用 HTML/Playwright/Crawl4AI 回退；
- 每家公司仍需独立小样本质量验收。

### OPS-002：独立调度与可观测性

- 增加独立 scheduler；
- 管理页显示下一次运行、最近成功、连续失败、退避和暂停原因；
- 支持人工启停，不支持并发批量强制抓取。

### UX-004：企业岗位状态

- 企业目录显示活动岗位数和最近更新时间；
- 点击有岗位企业进入筛选结果；
- 暂无岗位企业显示接入状态，不生成假岗位。

## 7. 发布指标

- 具体岗位误入率：0；
- 必填字段完整率：100%；
- 重复岗位率：低于 1%；
- 已接入来源的新岗位发现延迟：不超过 12 小时；
- 未变化岗位的详情重复请求率：接近 0；
- 空快照或骤降导致的有效岗位误下线：0；
- 403/429/验证码后的自动重试次数：0；
- 每个来源都有官方证据、fixture、运行记录和快照记录。

## 8. 下一执行单元

先实施 `D-007 增量更新内核`，完全使用本地数据库和合成 fixture，不访问任何招聘网站。通过后再选择一个飞书公开来源执行 `D-008` 的 20 条小样本验证。

