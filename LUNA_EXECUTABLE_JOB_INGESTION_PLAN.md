# 牛投马面：校招岗位采集与自动更新实施规格（Luna 可直接执行）

版本：V1.1  
适用目录：`F:\牛投马面\V0.1\graduate-jobs-mvp`  
目标：把企业官方公开校招岗位采集、标准化、增量更新并展示到“找岗位”。

> 本文是唯一执行入口。Luna 每完成一个执行单元，必须运行对应验证命令、更新 `EXECUTION_HARNESS_V03.md`，再继续下一个单元。不要一次性重写项目。

## 当前执行状态（2026-08-15）

以下状态来自当前数据库和最近 Harness 记录，接手执行时以数据库为准：

- 活动岗位：631 条；隔离岗位 6 条，被拒绝观察 4 条。
- 已有具体岗位适配器：小米、小鹏、叠纸、OPPO、米哈游、MiniMax（飞书通用适配器）。
- 已具备可复用的 Greenhouse 公共 jobs feed 适配器，但尚未绑定任何未经官方归属确认的企业来源。
- 当前已接入企业：小米 575 条、米哈游 20 条、叠纸 19 条、OPPO 7 条、小鹏 5 条、MiniMax 5 条。
- 已具备可复用的 Lever 公共 postings feed 适配器，但尚未绑定任何未经官方归属确认的企业来源。
- 米哈游最近一次受控样本：20 条，全部通过质量门禁；描述、任职要求、城市、学历和官方岗位链接齐全。
- 活动岗位招聘类型：只允许 `全职`、`实习`，当前无其他值。
- 360、腾讯：能发现岗位列表，但具体详情/投递链接证据不足，保持暂停。
- 字节跳动、完美世界、蔚来：最近受控探查超时，保持暂停，不得立即重试。
- 阿里、哔哩哔哩、华为、科大讯飞、美团等：已有 Harness 证据，按各自暂停原因处理，不重复盲目访问。
- 只有完成官方归属确认、详情字段验收和投递链接验收的来源，才允许进入自动调度。
- “找岗位”的企业目录现在会区分：已有具体岗位、已接入但暂无活动岗位、来源暂停、来源待验证；不要把注册表中的企业数量当成岗位数量。

### Luna 接手规则

1. 先读本文件、`EXECUTION_HARNESS_V03.md` 和数据库当前状态；以数据库为准，不把文档旧统计当成事实。
2. 每次只执行一个 `source_key`，每个执行单元结束后必须记录 Harness，再进入下一个来源。
3. 没有明确的企业官方归属和具体岗位详情/投递 URL，只能登记为候选或暂停，不能写入活动岗位。
4. 遇到 403、429、验证码、安全验证、登录墙或详情 URL 不可审计，立即停止该来源；不得自动重试或换路绕过。
5. 用户未要求扩大范围时，优先完善已有来源和通用 ATS；不要为了“数量”降低字段门禁。

## 1. 最终产品行为

“找岗位”只读取经过质量门禁的 `jobs` 数据，不直接读取企业入口页面。

每条活动岗位必须展示：

| 页面字段 | 数据字段 | 规则 |
|---|---|---|
| 公司 | `company` / `company_id` | 企业标准名称 |
| 城市 | `city` | 多城市用 ` / ` 分隔；未知为“未注明” |
| 职能 | `category` | 受控分类，不把原始长文本直接当分类 |
| 岗位 | `title` | 具体岗位名称，不能是招聘计划、活动或项目名称 |
| 招聘类型 | `job_nature` | 只能是 `全职` 或 `实习` |
| 学历要求 | `degree` | `未注明`、`大专及以上`、`本科及以上`、`硕士及以上`、`博士` |
| 岗位描述 | `description` | 企业官方原文 |
| 任职要求 | `requirements` | 企业官方原文 |
| 投递 | `apply_url` | 具体岗位详情或官方投递 URL |

禁止进入活动岗位表：招聘计划介绍、宣讲会、活动卡片、导航页、空详情、无法证明属于岗位的对象、无法确定招聘类型的对象。

## 2. 推荐的开源组合及边界

不要直接复制任何开源项目的企业脚本。借鉴其接口设计，并在本项目现有 Worker 和质量门禁上实现。

| 开源项目 | 借鉴内容 | 是否作为主采集器 |
|---|---|---|
| [Scrapy](https://github.com/scrapy/scrapy) | 请求调度、Item/Pipeline、重试和限速思想 | 暂不迁移；现有单来源 Worker 足够 |
| [ATS Job Scraper](https://github.com/YvetteZheng0812/ats-job-scraper) | Greenhouse、Lever、Ashby、Workday 等 ATS 的适配器抽象 | 借鉴适配器结构；必须自行确认企业官方归属 |
| [Crawl4AI](https://github.com/unclecode/crawl4ai) | 自建招聘站的动态页面内容提取 | 仅作为最后回退，不替代确定性接口适配器 |
| [changedetection.io](https://github.com/dgtlmoon/changedetection.io) | 页面变化监控思路 | 暂不引入；先用列表哈希和快照差异 |
| [JobSpy](https://github.com/speedyapply/JobSpy) | 岗位发现和字段启发 | 只能作为线索，不得作为官方岗位主数据 |
| [Campus-Jobs-Scraper](https://github.com/hunhunzhang/Campus-Jobs-Scraper) | 国内校招站点接口探查思路 | 只参考，不复制未确认许可证的代码 |

落地组合：

```text
现有 FastAPI + SQLite
    + source-specific adapter（公开 JSON 优先）
    + 单来源串行 Worker + source lock
    + 规则标准化 + 质量门禁
    + listing/detail 哈希 + 快照保护
    + 独立 scheduler 低频更新
    + Playwright 仅用于首次探查或确需 JS 的页面
```

## 3. 企业和招聘入口发现流程

大、中、小企业都按同一流程接入，规模只影响优先级，不降低数据质量门槛。

### 3.1 建立企业候选表

新增或维护 `data/company_candidates.csv`，字段：

```text
canonical_name,brand_name,official_website,discovery_source,industry,company_size,evidence_url
```

`company_size` 仅允许 `large`、`medium`、`small`、`unknown`。来源可以来自企业官网、上市公司公告、产业园目录、高校就业中心等，但候选记录不等于官方招聘入口。

### 3.2 确认官方招聘入口

对每家公司只做以下低频、串行检查：

1. 从企业官网进入“招聘 / 校招 / 加入我们 / Careers”。
2. 记录最终招聘域名、入口 URL 和证据 URL。
3. 识别 ATS 类型：飞书、北森、Moka、Greenhouse、Lever、Ashby、Workday 或 `custom`。
4. 只有能证明招聘入口属于该企业时，才标记 `official_status=confirmed`。
5. 发现阶段只写 `companies` 和 `career_sources`，绝不写 `jobs`。

禁止：扫描整个域名、猜测租户、暴力枚举岗位 ID、绕过验证码/登录/风控、使用代理池或指纹伪装。

建议复用现有：

```text
crawler/source_discovery.py
crawler/source_registry.py
config/sources.json
```

## 4. 统一采集适配器契约

每个企业或 ATS 只实现一个适配器，放在 `crawler/adapters/`。适配器不能直接写数据库，只返回标准中间对象。

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

采集顺序固定为：

```text
公开 JSON/API → 服务端 HTML → Playwright → Crawl4AI 回退
```

当列表接口已经包含描述和要求时，不逐条请求详情；只有新岗位、列表哈希变化或详情超过 7 天未刷新时才请求详情。每个来源单次最多 20 条小样本，确认通过后再由 scheduler 低频更新。

## 5. 岗位字段标准化

在 `crawler/normalize.py` 中集中实现，所有适配器必须调用，不能各自发明枚举。

### 5.1 招聘类型

```python
normalize_job_nature(raw_nature, title, description) -> str | None
```

规则：

- `实习 / 实习生 / intern / internship` → `实习`
- `全职 / 正式 / 校招 / 应届 / graduate / new grad / full-time` → `全职`
- 明确为社招、兼职、劳务、外包、博士专项等 → `None`
- 无法确定 → `None`，进入隔离，不猜成全职
- 同时有“校招/实习”时，按具体岗位的实习性质归为 `实习`

### 5.2 职能

`category` 只允许：

```text
算法/AI、软件研发、硬件研发、测试/质量、数据、产品、运营、设计、市场/销售、制造/工艺、供应链/采购、职能、其他
```

优先使用企业接口的明确职能；接口没有时使用标题和要求中的确定性关键词。LLM 只能补充解释或给出候选，不得凭空改写岗位原文。

### 5.3 学历

`degree` 只允许：

```text
未注明、大专及以上、本科及以上、硕士及以上、博士
```

从明确要求中提取：本科/学士 → `本科及以上`；硕士/研究生 → `硕士及以上`；博士 → `博士`。只有“优先、加分、优先考虑”时不要当硬门槛；多个学历取最低准入学历；无证据为 `未注明`。

### 5.4 城市、岗位和原文

- 城市删除“市、区”等冗余标签并去重，多城市用 ` / `。
- 标题保留方向和届次，不把公司名、招聘计划前缀重复拼入。
- `description`、`requirements` 必须来自企业页面/API 原文或确定性清洗结果。
- 不允许 LLM 编写不存在的职责、要求、城市、学历和投递链接。

## 6. 入库质量门禁

活动岗位至少满足：

```text
company_id
company
title
city
job_nature ∈ {全职, 实习}
category
degree
apply_url
source_url
description 或 requirements 至少一个非空
source_job_id 或稳定详情 URL
```

不满足的记录写入隔离/运行证据，不进入“找岗位”。错误详情链接、计划页链接、空详情必须拒绝。

岗位身份优先级：

```text
source_id + source_job_id
→ 规范化详情 URL
→ company + title + city + job_nature 的稳定指纹
```

同一岗位描述变化只能更新原记录，不能新增重复岗位。

## 7. 自动更新策略

在 `crawler/runner.py` 保留单次执行，在 `crawler/scheduler.py` 负责周期调度。Web 服务启动不能触发采集。

每次运行：

```text
获取 source lock
→ 检查 enabled / official_status / paused_reason / next_run_at
→ fetch_listing
→ 403/429/验证码/登录墙立即停止并暂停
→ 计算 listing_hash
→ 只对新增或变化岗位 fetch_detail
→ 标准化和质量门禁
→ upsert 同一岗位
→ 生成完整快照差异
→ 更新 crawl_runs、source_snapshots、source 状态
→ 释放锁
```

更新规则：

- 默认间隔 12 小时；近期有变化可缩短到 6 小时。
- 同一来源串行，单次最多 20 条，适当请求间隔，不并发轰击。
- 使用 ETag/Last-Modified（服务端支持时）和列表哈希减少无效请求。
- 一次岗位消失不下线；连续 3 次健康完整快照都缺失才标记 `inactive`。
- 空快照或岗位数骤降超过 50% 触发保护，不覆盖当前有效岗位。
- 普通失败指数退避；403、429、验证码、安全验证、登录墙不重试，直接暂停等待人工复核。

命令：

```powershell
python -m crawler.source_registry --source-file config/sources.json
python -m crawler.worker --source <source-key>
python -m crawler.scheduler --once
python -m crawler.scheduler --loop
```

## 8. 接入新企业的执行单元

每家企业都必须按以下 8 个单元执行，不允许跳过验收：

### S1 入口确认

修改 `config/sources.json`，注册为 `candidate / analyzing`，不采集岗位。记录官方归属证据。

验收：企业官网能导航到招聘入口；URL、ATS 类型、校招范围有记录。

### S2 本地 fixture

新增 `tests/fixtures/<source-key>/listing.json` 和必要的 `detail-*.json`。fixture 不得访问网络。

验收：能解析具体岗位、非岗位对象会被拒绝。

### S3 适配器

新增 `crawler/adapters/<source>.py`，限制最多 20 条，使用已确认公开接口或页面。

验收：列表、详情 URL、全职/实习转换正确。

### S4 标准化测试

新增 `tests/test_<source>_adapter.py`，覆盖城市、职能、学历、描述、要求和招聘类型。

验收：招聘类型除全职/实习外全部拒绝；不访问网络。

### S5 单次真实小样本

只运行一次该来源，最多 20 条；出现 403、429、验证码或登录墙立即停止并暂停。

验收：字段完整率 100%，计划/活动误入 0，重复岗位为 0。

### S6 入库和前端

通过现有 runner/upsert 写入后，确认 `/api/jobs` 和“找岗位”能按企业、城市、职能、招聘类型、学历筛选。

验收：新岗位无需改静态页面即可出现；详情和官方投递链接可打开。

### S7 调度资格

只有 S5、S6 全部通过且官方归属确认，才把来源改为 `confirmed / integrated`。否则保持候选或暂停。

### S8 Harness 记录

在 `EXECUTION_HARNESS_V03.md` 记录：时间、来源、请求数量、岗位数量、接受数、隔离数、失败原因、保护动作、测试结果、下一步。

## 9. 必须修改/新增的文件

优先复用现有实现，只有缺失时才修改：

```text
crawler/adapters/base.py             统一契约
crawler/adapters/<source>.py         企业专用适配器
crawler/normalize.py                 统一字段枚举
crawler/runner.py                    采集、门禁、upsert
crawler/worker.py                    单来源执行
crawler/scheduler.py                 低频增量调度
crawler/source_discovery.py          企业入口发现
crawler/source_registry.py           来源注册
config/sources.json                  企业来源配置
tests/fixtures/<source-key>/*        脱敏 fixture
tests/test_<source>_adapter.py       适配器测试
tests/test_normalize.py               标准化测试
EXECUTION_HARNESS_V03.md             每次执行记录
```

不要为了接入一家企业重写数据库、前端、推荐系统或整个 Scrapy 工程。

## 10. 交付验收命令

每个执行单元结束时执行：

```powershell
python -m compileall app crawler tests
pytest -q
Invoke-WebRequest http://127.0.0.1:8000/health
Invoke-WebRequest 'http://127.0.0.1:8000/api/jobs?limit=20'
```

验收指标：

- 活动岗位 `job_nature` 只出现全职、实习；
- 必填字段完整率 100%；
- 计划/活动/空详情误入率 0%；
- 同来源同岗位重复率低于 1%；
- 采集失败不污染已有岗位；
- 403/429/验证墙后自动重试次数为 0；
- 新岗位在成功入库后出现在“找岗位”；
- 所有真实运行都有 Harness 记录。

## 11. 开源方案的实际取舍

不要把多个爬虫框架拼成一个大系统，按下面的方式落地：

| 场景 | 采用 | 实际动作 |
|---|---|---|
| 公开 JSON/ATS Feed | 现有 Python adapter | 直接请求公开接口，保存岗位 ID、详情 URL、响应哈希 |
| 服务端 HTML | 现有 HTML adapter | 解析可见岗位卡和详情页，不解析导航/计划卡 |
| 必须执行 JS 的公开页面 | Playwright | 只用于受控探查或低频抓取，不用于绕过验证 |
| 页面变化判断 | listing/detail hash | 未变化时不请求详情，变化时只更新新增/变化岗位 |
| 企业和岗位线索发现 | JobSpy、New-Grad-Positions 等 | 只生成候选线索，必须回到企业官网复核，不能作为主数据 |
| 大规模通用调度 | Scrapy（未来可选） | 当前不迁移；来源达到数百且现有 Worker 成为瓶颈时再评估 |

验收标准不是“抓到多少页面”，而是“多少条可审计的具体岗位”。

## 12. 推荐的企业扩展顺序

按成功率和复用价值排序，不按公司规模盲目排序：

1. 已确认使用 Greenhouse、Lever、Ashby、Workday 公共 feed 的企业；
2. 已确认使用飞书、北森、Moka 且公开岗位详情完整的企业；
3. 已有稳定岗位卡和详情 URL 的大型企业自建站；
4. 中型企业自建站；
5. 小型企业官网、园区/高校公开招聘页。

每批最多接入 1 个来源，验收通过后再接入下一个。企业规模只影响优先级，不改变字段质量门禁。

## 13. 给 Luna 的直接执行模板

```text
目标来源：<source-key>

1. 读取 config/sources.json、数据库来源状态和最近 Harness。
2. 验证企业官网到招聘入口的官方归属，只做一次低频访问。
3. 识别 ATS；优先复用现有 adapter，不能确定就登记 candidate/analyzing。
4. 用脱敏 fixture 编写解析测试，至少覆盖：具体岗位、计划卡、未知招聘类型、无详情 URL、全职、实习。
5. 运行 compileall、适配器测试和全量测试。
6. 真实页面最多采集 20 条，串行执行；遇保护信号立即暂停。
7. 通过质量门禁后写入 jobs；失败记录写入 quarantine/run evidence，不污染有效岗位。
8. 检查 /api/jobs、/api/facets、前端筛选和详情/投递链接。
9. 只有 S1-S8 全部通过才启用调度；否则保留 candidate 或 paused。
10. 更新 EXECUTION_HARNESS_V03.md，写清接受数、隔离数、失败原因和下一步。
```

### 推荐的首个最小执行单元

先选一个“官方归属明确、公开详情 URL 明确、无需登录”的候选来源，完成 S1-S8；不要同时新增多个企业。若已有 Greenhouse/Lever 归属证据，优先验证通用 ATS adapter；否则优先选择页面结构稳定的企业自建站。

## 14. 最终交付物清单

Luna 完成一轮后，必须留下以下结果：

- 企业候选表：公司规模、官网、招聘入口、官方证据和当前状态；
- 来源配置：ATS、适配器、更新间隔、暂停原因和下一次运行时间；
- 岗位数据：每条具备公司、城市、职能、岗位、招聘类型、学历、描述/要求和官方投递链接；
- 前端结果：在“找岗位”按公司、城市、职能、全职/实习、学历可以检索，点击可查看详情并跳转官方投递；
- 更新结果：新增岗位进入列表，变化岗位原地更新，短暂缺失不立即下线，异常快照不覆盖旧数据；
- 运行证据：每个来源都有可追溯的 Harness 记录和测试结果。

明确不做：不把企业注册表直接当成岗位数据；不把招聘计划、宣讲会、活动页当成岗位；不把社招、兼职、外包或无法判断强行映射成全职；不使用代理池、指纹伪装、验证码绕过、登录墙绕过或岗位 ID 猜测；不让 AI 编造城市、学历、职责、要求或投递链接。

## 11. Luna 执行指令

```text
进入 F:\牛投马面\V0.1\graduate-jobs-mvp。
阅读 LUNA_EXECUTABLE_JOB_INGESTION_PLAN.md，并严格按 S1→S8 执行。
先检查当前代码、数据库和测试，不重复实现已有能力。
每次只处理一个来源、最多 20 条真实岗位；测试优先使用本地 fixture。
任何 403、429、验证码、登录墙或详情链接不确定，立即停止该来源并记录原因，不重试、不绕过。
每个单元完成后运行验收命令，更新 EXECUTION_HARNESS_V03.md，再继续下一单元。
不要删除历史岗位、失败记录、隔离记录或用户数据；不要把密钥写入代码、日志或文档。
```
