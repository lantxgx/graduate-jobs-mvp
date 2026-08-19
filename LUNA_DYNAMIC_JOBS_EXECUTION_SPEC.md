# Luna 可直接执行：校招岗位动态采集与产品接入规格

版本：V0.3

日期：2026-08-15

项目目录：`F:\牛投马面\V0.1\graduate-jobs-mvp`

## 0. 执行总要求

在当前项目内连续执行本规格，不重写现有产品，不删除历史失败记录、隔离记录或用户已有数据。每个单元完成后运行全套测试、审计数据库、更新 `EXECUTION_HARNESS.md`；没有外部卡口时继续下一单元。

执行顺序：

```text
D-007 → D-008 → D-009 → D-010 → D-011 → OPS-002 → UX-004 → R-003
```

安全约束：

- 真实网站一次只访问一个来源，低频、串行、无自动重试；
- 403、429、验证码、安全验证或登录墙立即停止并暂停来源；
- 不使用代理池、指纹伪装、验证码绕过、账号登录或租户暴力枚举；
- 自动测试只使用本地脱敏 fixture；
- 外部模型只处理单条脱敏岗位文本，不接收 Cookie、Token 或完整网站响应；
- `.env` 密钥不得写入代码、日志、测试、文档和 Harness。

## 1. 产品完成定义

前端每条岗位必须包含：

| 产品字段 | 数据库字段 | 规则 |
|---|---|---|
| 公司 | `company`、`company_id` | 企业标准名称 |
| 城市 | `city` | 多城市用 ` / ` 分隔 |
| 职能 | `category` | 受控职能分类 |
| 岗位 | `title` | 具体岗位名称 |
| 招聘类型 | `job_nature` | 只能是 `全职` 或 `实习` |
| 学历要求 | `degree` | 受控学历枚举 |
| 职位描述 | `description` | 原始证据，不允许模型编造 |
| 任职要求 | `requirements` | 原始证据，不允许模型编造 |
| 官方投递 | `apply_url` | 具体岗位详情或投递地址 |

V0.3 必须满足：

- 所有活动岗位的招聘类型只包含全职、实习；
- 新岗位成功采集后自动出现在 `/api/jobs` 和首页；
- 已有岗位变化时更新原记录，不创建重复岗位；
- 岗位一次消失不会立即下线；
- 招聘计划、活动介绍、宣讲会、导航卡片、空详情不会进入活动岗位；
- 至少打通一种可复用 ATS，并完成一家企业最多 20 条真实小样本验收。

## 2. 开源方案选择

保留当前 FastAPI、SQLite、Playwright、单来源 Worker、来源锁和质量门槛。局部借鉴：

| 项目 | 用途 | 采用方式 |
|---|---|---|
| [Scrapy](https://github.com/scrapy/scrapy) | HTTP 采集与 Pipeline | 当前不迁移；来源达到数百个后再评估 |
| [Crawl4AI](https://github.com/unclecode/crawl4ai) | 动态自建招聘页面 | 仅作为自建页面回退 |
| [changedetection.io](https://github.com/dgtlmoon/changedetection.io) | 页面变化监控 | 暂不部署，先使用现有内容哈希和快照 |
| [ATS Job Scraper](https://github.com/YvetteZheng0812/ats-job-scraper) | Greenhouse、Lever、Workday 等 ATS | 借鉴 MIT 项目的适配器接口和公开 ATS 获取方式 |
| [JobSpy](https://github.com/speedyapply/JobSpy) | 第三方招聘平台 | 只做企业和入口线索，不作为官方岗位主数据源 |
| [Campus Jobs Scraper](https://github.com/hunhunzhang/Campus-Jobs-Scraper) | 字节、腾讯、美团、米哈游脚本 | 未声明许可证，不复制代码，只参考接口识别思路 |
| [SimplifyJobs/New-Grad-Positions](https://github.com/SimplifyJobs/New-Grad-Positions) | 海外企业线索 | 只做发现，必须回到企业官网验证 |

结论：国内飞书、北森、Moka 没有已验证的成熟统一开源项目。核心必须是“ATS 通用适配器 + 企业配置”，通用页面抽取只能作为回退。

## 3. 大、中、小企业招聘入口发现

### 3.1 企业候选

新增 `data/company_candidates.example.csv` 和导入命令。候选来源：

- 大型企业：上市公司、行业龙头、500 强、现有 52 家企业；
- 中型企业：专精特新、融资企业、产业协会、产业园公开目录；
- 小型企业：孵化器、开发区、技术社区、高校就业中心公开企业名单；
- 海外企业：公开 New Grad 社区列表，仅作为线索。

CSV 字段：

```text
canonical_name,brand_name,official_website,discovery_source,industry,company_size,evidence_url
```

`company_size`：`large`、`medium`、`small`、`unknown`。

### 3.2 招聘入口发现

对每家企业执行：

1. 检查企业官网页脚和 `招聘`、`加入我们`、`校园招聘`、`careers` 链接；
2. 可选通过合规搜索 API 查询企业名与校招关键词；
3. 搜索结果只能创建 `candidate` 来源；
4. 有官网跳转或可验证品牌/域名证据后才能标记 `confirmed`；
5. 不扫描域名段，不枚举 ATS 租户。

新增 `crawler/source_discovery.py`：

```python
def import_company_candidates(path: Path) -> ImportResult: ...
async def discover_official_career_links(company: dict) -> list[SourceCandidate]: ...
def classify_ats(url: str, page_title: str = "", html: str = "") -> str: ...
def verify_official_ownership(company: dict, candidate: dict) -> EvidenceResult: ...
```

ATS 域名规则至少覆盖：

```text
jobs.feishu.cn / jobs.f.mioffice.cn → feishu
*.zhiye.com → beisen
*.mokahr.com → moka
greenhouse.io → greenhouse
lever.co → lever
ashbyhq.com → ashby
myworkdayjobs.com → workday
其他 → custom
```

发现阶段只写 `companies` 和 `career_sources`，绝不写 `jobs`。

## 4. 数据库改造

修改 `app/db.py`，使用幂等建表和非破坏性迁移。

### 4.1 企业别名

新增：

```sql
CREATE TABLE IF NOT EXISTS company_aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    alias TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(company_id) REFERENCES companies(id)
);
```

写入 `canonical_name`、非空 `brand_name` 及当前已知映射，例如“小米集团 → 小米”“小鹏集团 → 小鹏”。长期关联必须查别名表，不能依赖模糊前缀。

### 4.2 岗位稳定身份

为 `jobs` 增加：

```text
company_id INTEGER
detail_hash TEXT
listing_hash TEXT
detail_fetched_at TEXT
missing_snapshot_count INTEGER NOT NULL DEFAULT 0
last_changed_at TEXT
```

新增部分唯一索引：

```sql
CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_source_job_identity
ON jobs(source_id, source_job_id)
WHERE source_job_id IS NOT NULL AND TRIM(source_job_id) <> '';
```

修改 `upsert_job()`：

1. 优先按 `source_id + source_job_id` 查找；
2. 没有来源岗位 ID 时才按规范化详情 URL或 `content_hash` 回退；
3. 详情变化时更新同一行和 `last_changed_at`；
4. 成功出现时重置 `missing_snapshot_count=0`；
5. 不允许因描述变化创建重复岗位。

### 4.3 来源调度字段

为 `career_sources` 增加：

```text
adapter TEXT
adapter_config_json TEXT
update_interval_seconds INTEGER NOT NULL DEFAULT 43200
next_run_at TEXT
last_attempt_at TEXT
last_success_at TEXT
consecutive_failures INTEGER NOT NULL DEFAULT 0
paused_reason TEXT
```

`adapter_config_json` 只能保存非敏感配置。

## 5. 字段标准化

修改 `crawler/normalize.py`，所有适配器写库前必须调用统一标准化。

### 5.1 招聘类型只允许全职或实习

新增：

```python
def normalize_job_nature(raw_nature: str | None, title: str, description: str = "") -> str | None:
    ...
```

规则：

1. `实习`、`实习生`、`intern`、`internship` → `实习`；
2. `全职`、`正式`、`校招`、`校园招聘`、`应届`、`graduate`、`new grad`、`full-time` → `全职`；
3. 同时存在校招父类和实习子类，例如 `校招 / 实习` → `实习`；
4. 明确社招、兼职、劳务、外包 → `None` 并拒绝进入活动校招岗位；
5. 无法判断 → `None`，进入隔离/待审核，不能猜测为全职。

迁移现有数据：小米 `校招 / 实习` → `实习`；小鹏 `正式` → `全职`。无法可靠映射的活动记录隔离但不删除。迁移前后岗位总数保持不变。

### 5.2 职能

数据库继续使用 `category`，前端标签统一为“职能”。受控枚举：

```text
算法/AI
软件研发
硬件研发
测试/质量
数据
产品
运营
设计
市场/销售
制造/工艺
供应链/采购
职能
其他
```

新增 `normalize_category(raw_category, title, description)`。优先使用 ATS 明确分类，再用确定性关键词。Qwen 只可在规则返回“其他”时补充，输出必须限制在枚举中并保留证据。

### 5.3 学历要求

新增 `normalize_degree(raw_degree, requirements)`，受控值：

```text
未注明
大专及以上
本科及以上
硕士及以上
博士
```

规则：本科/学士 → 本科及以上；硕士/研究生 → 硕士及以上；博士研究生 → 博士；多个学历取最低准入学历；原文无要求 → 未注明；“优先”不能解释为硬门槛。

### 5.4 城市、公司、岗位

- 城市去除标签，多城市去重后用 ` / ` 分隔；
- 公司通过 `company_id` 和别名表映射；
- 标题保留方向和届别，去除重复企业前缀；
- 招聘计划、项目介绍、宣讲会、隐私政策、报名入口不属于岗位。

## 6. 统一 ATS 适配器

新增：

```text
crawler/adapters/__init__.py
crawler/adapters/base.py
crawler/adapters/feishu.py
crawler/adapters/beisen.py
crawler/adapters/moka.py
crawler/adapters/greenhouse.py
crawler/adapters/lever.py
crawler/adapters/workday.py
crawler/adapters/custom.py
```

当前已落地的专用适配器还包括 `crawler/adapters/papegames.py` 和 `crawler/adapters/oppo.py`：它们读取公开岗位列表响应，最多取 20 条，不对每条岗位再发详情请求；列表项本身必须包含具体岗位描述或要求。

`base.py` 定义统一接口：

```python
@dataclass
class ListingItem:
    source_job_id: str
    title: str
    detail_url: str
    raw: dict

@dataclass
class CollectionResult:
    listing_items: list[ListingItem]
    snapshot_complete: bool
    response_urls: list[str]
    stop_reason: str | None = None

class JobSourceAdapter(Protocol):
    async def fetch_listing(self, source: dict) -> CollectionResult: ...
    async def fetch_detail(self, source: dict, item: ListingItem) -> dict: ...
    def normalize(self, source: dict, raw: dict) -> dict | None: ...
```

获取顺序：公开 JSON → 服务端 HTML → 必须执行 JavaScript 时用 Playwright → 自建页面最后使用 Crawl4AI 风格抽取。浏览器发现只用于首次确认公开接口，不在每次更新时重复发现。

每个适配器必须提供本地脱敏 fixture 和离线测试。

## 7. 增量采集和自动更新

重构 `crawler/runner.py`，保留现有入口兼容性。

单次运行：

```text
读取一个来源
→ 获取来源锁
→ 检查冷却、暂停和 next_run_at
→ fetch_listing
→ 停止信号立即失败并暂停
→ 按 source_job_id 去重
→ 只对新增或列表摘要变化的岗位 fetch_detail
→ 统一字段标准化
→ 具体岗位质量门槛
→ upsert 同一岗位
→ 完整快照差异
→ 记录 snapshot 和 crawl_run
→ 更新来源调度状态
→ 释放锁
```

`listing_hash` 基于：

```text
source_job_id,title,city,job_nature,detail_url,listing_updated_at
```

只有新岗位、摘要变化或详情超过 7 天未刷新时才请求详情；未变化岗位只更新 `last_seen_at`，不调用 Qwen。

岗位消失：第一次、第二次完整健康快照缺失只增加 `missing_snapshot_count`；第三次才设为 `inactive`。任意再次出现立即清零并恢复活动。空快照或比上次下降超过 50% 时保护，不增加缺失次数。

活动岗位质量门槛：

```text
company_id
company
title
city
job_nature ∈ {全职, 实习}
category
degree
source_job_id 或稳定详情 URL
apply_url
source_url
description 或 requirements
content_hash
```

不合格记录进入隔离/运行证据，不进入活动岗位。

## 8. 独立调度器

新增 `crawler/scheduler.py`，不能在 FastAPI startup 中循环调度。

选择条件：

```text
enabled=1
official_status='confirmed'
access_status='reachable'
integration_status='integrated'
paused_reason IS NULL
next_run_at <= now
```

间隔：近期有变化 6 小时；正常无变化 12 小时；30 天无岗位 24 小时；普通失败按 1、3、12、24 小时退避；403/429/验证码/登录墙直接暂停。

一次只运行一个来源，增加 0～10 分钟随机抖动。CLI：

```powershell
python -m crawler.scheduler --once
python -m crawler.scheduler --loop
python -m crawler.worker --source <source-key>
```

## 9. API 和找岗位页面

保留 `/api/jobs`。新增：

```text
GET /api/companies/{company_id}/jobs
GET /api/companies/{company_id}/collection-status
GET /api/job-updates?since=<ISO timestamp>&limit=100
```

修改 `static/index.html`、`static/app.js`：

- `category` 标签改为“职能”；
- 招聘类型下拉框固定为“全部类型、全职、实习”，不从脏数据生成其他值；
- 岗位卡固定展示公司、城市、职能、岗位、招聘类型、学历要求；
- 学历缺失显示“未注明”；
- 企业目录显示活动岗位数、最近成功时间、接入状态；
- 点击有岗位企业直接筛选；
- 无岗位企业显示“暂无已验证岗位”，不生成假岗位。

管理页显示 adapter、最近成功、下一次运行、连续失败、暂停原因、最近快照发现数、合格数和保护原因。

## 10. 执行单元和验收

### D-007：字段、企业和岗位身份标准化

修改：`app/db.py`、`crawler/normalize.py`、`tests/test_normalize.py`，新增 `tests/test_job_identity.py`、`tests/test_data_migration.py`。

验收：520 条总记录迁移前后不变；507 条活动岗位招聘类型只包含全职/实习；同一 `source_job_id` 描述变化不增加记录。

### D-008：三次缺失和快照保护

修改：`app/db.py`、`crawler/runner.py`，新增 `tests/test_snapshot_diff.py`。

验收：第三次连续完整健康快照缺失才下线；空快照和骤降不累计缺失。

### D-009：企业候选和招聘入口发现

新增 `crawler/source_discovery.py`、`data/company_candidates.example.csv`、`tests/test_source_discovery.py`，更新 `crawler/company_directory.py`。

验收：可导入大中小企业候选；ATS 分类正确；未确认官方的入口不能进入自动队列。

### D-010：统一适配器框架

新增 `crawler/adapters/*` 和 `tests/fixtures/*`，重构 `crawler/runner.py`。

验收：现有小米、小鹏、北森 fixture 通过统一接口；全套测试不访问网络。

### D-011：首个真实 ATS 小样本

选择一个已确认官方、公开可访问、无需登录且冷却已结束的来源，一次最多 20 条，无重试。

验收：字段完整率 100%；导航卡片误入 0；类型只有全职/实习；首页可按企业筛选；失败不污染岗位库。

### OPS-002：独立调度

实现 scheduler、退避、暂停和管理页状态。API 服务重启不得触发采集，重复任务必须被来源锁阻止。

### UX-004：找岗位字段闭环

固定展示公司、城市、职能、岗位、招聘类型和学历；招聘类型筛选只有全职/实习。

### R-003：全链路回归

```text
候选企业导入
→ 官方入口确认
→ ATS 小样本
→ 质量门槛
→ 增量写库
→ /api/jobs 分页
→ 企业/城市/职能/全职实习/学历筛选
→ 岗位详情与官方投递
→ 管理页运行和快照证据
```

## 11. 必须增加的测试

1. `校招 / 实习` → `实习`；
2. `正式`、`校园招聘`、`Graduate` → `全职`；
3. 社招、兼职、外包不进入活动岗位；
4. 未知招聘类型被隔离；
5. 学历枚举和“优先”非硬条件；
6. 12 类职能映射；
7. 小米集团、小米映射到同一 company_id；
8. source_job_id 相同、描述变化时原行更新；
9. 第三次连续缺失才失效；
10. 空快照和 50% 骤降保护；
11. 飞书、北森、Moka fixture；
12. 403/429/验证码/登录墙停止；
13. scheduler 只选到期且已集成来源；
14. `/api/jobs` 类型只有全职/实习；
15. 前端固定展示六个核心字段。

## 12. Harness 记录

每单元追加：状态、输入基线、修改文件、迁移前后数量、测试结果、真实访问次数和上限、字段完整率、导航卡片误入、重复岗位、招聘类型枚举、保护动作、结论和下一单元。禁止覆盖历史失败；禁止把“入口已发现”描述成“岗位已接入”。

## 13. 可直接复制给 Luna 的提示词

```text
请在 F:\牛投马面\V0.1\graduate-jobs-mvp 中连续实施校招岗位动态采集 V0.3。

完整读取并严格执行 LUNA_DYNAMIC_JOBS_EXECUTION_SPEC.md，同时遵守 AGENTS.md 和现有 EXECUTION_HARNESS.md。执行顺序：D-007 → D-008 → D-009 → D-010 → D-011 → OPS-002 → UX-004 → R-003。

关键约束：
1. 找岗位固定展示公司、城市、职能、岗位、招聘类型、学历要求；
2. 招聘类型只能是“全职”或“实习”，无法判断的岗位不得进入活动岗位库；
3. 企业入口不是岗位，只有通过具体岗位质量门槛的数据才能进入 /api/jobs；
4. 岗位按 source_id + source_job_id 稳定更新，详情变化不得创建重复岗位；
5. 连续三次完整健康快照缺失后才能下线；空快照和骤降必须保护；
6. 自动测试只使用本地 fixture；
7. 真实网站一次只验证一个官方公开来源，最多 20 条、串行、无重试；403、429、验证码、安全验证、登录墙立即停止；
8. 不绕过访问控制，不使用代理池或指纹伪装；
9. 每单元完成后运行全套测试、审计数据库、追加 Harness；无外部卡口时继续；
10. 不删除历史失败、隔离数据和用户数据，不泄露 .env 密钥。

先执行 D-007，通过后自动进入 D-008。D-011 只有在前置离线单元全部通过、来源官方性和公开访问已确认时才执行。
```
