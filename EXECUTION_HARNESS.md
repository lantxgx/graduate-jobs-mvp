# AI 校招岗位匹配平台：执行 Harness

最近更新：2026-08-15

## 1. Harness 规则

每次只执行一个最小单元。每个单元必须记录：目标、范围、输入、产出、依赖卡口、验收标准、运行记录、问题和结论。

状态仅使用：`待执行`、`执行中`、`待反馈`、`需修改`、`已通过`、`被阻塞`。

执行流程：

1. 检查开始条件和上游卡口。
2. 将单元标记为 `执行中`。
3. 完成范围内的最小改动，不顺带扩展功能。
4. 运行自动检查、数据检查和人工可见检查。
5. 追加运行记录，不覆盖失败历史。
6. 有问题则进入 `需修改`；需要产品决策则进入 `被阻塞`。
7. 自动验收通过后进入 `已通过`，并继续执行不依赖外部决策的下一单元。
8. 只有产品决策、凭据、真实来源授权或高风险失败才暂停并进入 `被阻塞`/`需修改`。

详细产品方向见 [DEVELOPMENT_OUTLINE.md](DEVELOPMENT_OUTLINE.md)，统一卡口见 [GATE_ANALYSIS.md](GATE_ANALYSIS.md)，Luna 开发交接见 [LUNA_IMPLEMENTATION_SPEC.md](LUNA_IMPLEMENTATION_SPEC.md)。

## 2. 当前基线

- [x] 本地服务、SQLite、API 和数据验收网页可运行。
- [x] 已发现 52 家企业、61 个候选招聘入口。
- [x] 小米已有 502 条具体实习岗位。
- [x] 小鹏 5 条岗位完成端到端验证。
- [x] 360、北森完成具体岗位小样本结构验证。
- [x] 远景动力数据已判定不可信并暂停。
- [x] 52 家企业、60 条去重入口已进入系统注册表。
- [x] 509/520 条岗位已归入统一岗位族，11 条保留 unknown。
- [x] 已建立能力画像、求职意愿、四类推荐池和反馈状态。
- [x] 当前基线为 520 条总记录、507 条活动岗位、6 条隔离记录、10 次运行、40/40 测试。
- [x] 用户首页、画像页和采集管理页已拆分。
- [x] 已证明全部 507 条活动岗位可通过稳定分页完整访问。
- [ ] 真实 Luna 端点尚未配置，真实外部模型验收未进行。

历史证据：

- [SMALL_SAMPLE_VALIDATION.md](SMALL_SAMPLE_VALIDATION.md)
- [MU001_RUN_HISTORY.md](MU001_RUN_HISTORY.md)

## 3. 主动执行队列

| 单元 | 目标 | 当前状态 | 开始条件 |
|---|---|---|---|
| UX-002 | 前后台与画像页面拆分 | 已通过 | 当前集成基线通过 |
| UX-003 | 全部岗位分页和完整详情 | 已通过 | UX-002 通过 |
| P-003 | 画像四步引导和确认闭环 | 已通过 | UX-002 通过 |
| M-005 | 30+ 案例推荐离线评测与校准 | 已通过 | UX-003、P-003 通过 |
| P-004 | 真实 Luna 结构化分析验收 | 被阻塞 | 用户提供兼容端点、模型和密钥 |
| D-006 | 逐家扩展真实具体岗位 | 被阻塞 | 单来源官方/合规/冷却卡口通过 |
| OPS-001 | 独立采集任务与可观测性 | 已通过 | 至少一个新增来源小样本通过 |
| R-002 | V0.2 产品发布验收 | 待反馈 | 所有非阻塞 P0 单元通过 |

## 4. 当前单元：UX-002 前后台与画像页面拆分

状态：`已通过`

目标：把当前单页中职责不同的三个区域拆成用户岗位页、画像页和内部数据管理页。

范围：

- `/` 只保留岗位搜索、推荐、详情和反馈状态。
- `/profile` 承载简历、能力证据和求职意愿。
- `/admin/sources` 承载企业入口、接入队列、运行记录和岗位质量。
- 复用现有 API，迁移现有功能，不触发真实采集、不修改岗位数据。

依赖卡口：

- G-RECALL-01 完整岗位入口
- G-PROFILE-01 解析结果确认
- G-PROFILE-02 能力与意愿分离

验收标准：

- [x] 三个页面路由均返回 200。
- [x] 首页不再展示企业注册表明细和简历表单。
- [x] 画像现有能力全部迁移且能力/意愿仍分离。
- [x] 管理页能看到来源统计、入口表、接入队列、运行和质量状态。
- [x] 原有 API 和 38 个测试不回归，JavaScript 语法检查通过。
- [x] 岗位表和采集运行基线不改变，本单元无招聘官网访问。

完整范围、文件更新和后续连续执行顺序见 [PRODUCT_V0_2_IMPLEMENTATION_PLAN.md](PRODUCT_V0_2_IMPLEMENTATION_PLAN.md) 与 [LUNA_IMPLEMENTATION_SPEC.md](LUNA_IMPLEMENTATION_SPEC.md)。

## 5. 运行记录

### PLAN-001 / 产品方向收敛

- 日期：2026-08-14
- 状态：已通过
- 产出：统一开发大纲、完整卡口分析和精简后的 Harness。
- 删除：过时的需求探索、旧结果说明和重复产品蓝图。
- 保留：源代码、数据库、原始压缩包、小样本验证和 MU-001 运行历史。
- 结论：产品方向和三个关键决策已确认，D-001 已解锁。

### DECISION-001 / 产品决策锁定

- 日期：2026-08-14
- 状态：已通过
- 简历保存：原始简历默认不长期保存，用户主动选择后才保存结构化画像。
- 推荐策略：默认 50% 主攻、25% 目标企业、20% 相邻、5% 探索。
- 竞争风险：只显示高/中/低和依据，不展示上岸概率。
- 结论：后续模型和开发人员不得自行修改这些默认策略；需要变化时必须产生新的决策记录。

### RUN-D001-001 / 企业数据源注册表导入

- 日期：2026-08-14
- 状态：待反馈
- 目标：导入企业与官方校招入口目录，建立后续接入控制面。
- 输入：`outputs/019fe088-133d-7612-8425-8d152dbf8426/official_campus_career_sites.xlsx`
- 实现：新增 `companies`、`career_sources` 表；新增幂等导入命令 `python -m crawler.company_directory`；新增只读 API `/api/companies`、`/api/company-sources`、`/api/company-source-stats`。
- dry-run：原始目录 61 行中识别 60 条去重入口、52 家企业、3 条排除记录；ATS 分类为 self_hosted 49、moka 4、feishu 4、beisen 2、other 1。
- 导入结果：首次创建 52 家企业、60 条入口；第二次创建 0 家企业、0 条入口，更新 60 条入口，幂等验证通过。
- 数据统计：确认官方入口 3、候选/未验证 54、可访问 48、异常或阻断 7。
- 数据保护：导入前后岗位表均 520 行、活动岗位均 513 条、`crawl_runs` 均 7 条；岗位内容摘要未发生变化。
- 自动化验收：`unittest tests.test_company_directory` 2/2 通过；Python 语法检查通过。
- 合规边界：本轮未访问任何招聘官网，未运行岗位采集器，未修改现有岗位数据。
- 问题与结论：入口目录存在重复 URL，因此系统按规范化 URL 去重；3 条排除项仍保留在数据库并标记 `excluded`。D-001 完成，等待用户反馈。


### RUN-D002-001 / ???????????????????

- ???2026-08-14
- ??????
- ????????????????????????????
- ???D-001 ???? 60 ????????????????ATS ???
- ????? `quality_level` ? `integration_priority` ??????? high?medium?low?blocked???? 0-4??????????? API ?????
- ??????????? high/P0?????????? ATS ? medium/P1???????? medium/P2?????????? low/P3???????????? blocked/P4?
- ???high 3?medium 45?low 2?blocked 10?P0 3?P1 4?P2 41?P4 12?
- ???`unittest tests.test_company_directory` 3/3 ???API ?? `quality_level=high&integration_priority=0` ?? 3 ??
- ??????????????????????????????
- ?????????????????????????????????????D-002 ??????????

### RUN-D002-001 / Source quality and integration priority (canonical record)

- Date: 2026-08-14
- Status: Pending feedback
- Scope: classify the 60 deduplicated career sources imported by D-001.
- Implementation: added `quality_level` and `integration_priority` to `career_sources`; added API filters.
- Result: high 3, medium 45, low 2, blocked 10; P0 3, P1 4, P2 41, P4 12.
- Verification: `unittest tests.test_company_directory` 3/3 passed; API high/P0 filter returned 3 sources.
- Boundary: no recruitment website access, no job crawler execution, and no job data changes.
- Conclusion: D-002 is complete and waiting for feedback.

### RUN-D004-001 / Feishu adapter reuse

- Date: 2026-08-15
- Status: Completed
- Scope: validate the existing Feishu detail parser against a second company layout.
- Verification: the parser accepts both four-line and compact two-line header layouts; 8/8 tests passed after the D-005 additions.
- Boundary: fixture-only validation; no live recruitment website access.

### RUN-D005-001 / Snapshot and anomaly protection

- Date: 2026-08-15
- Status: Pending feedback
- Implementation: added `source_snapshots`, `/api/source-snapshots`, snapshot content hashes, empty-result protection, and over-50-percent sudden-drop protection.
- Behavior: a complete source snapshot is not allowed to deactivate historical jobs when it is empty or drops by more than 50 percent from the previous qualified snapshot.
- Verification: empty, sudden-drop, and normal-count cases passed; full test suite is 8/8.
- Boundary: no live crawl was run and existing job rows were not changed.

### RUN-P001-001 / Manual profile and job-seeking intent

- Date: 2026-08-15
- Status: Completed
- Implementation: added structured profile storage and `/api/profile` GET/PUT/DELETE endpoints; added the editable profile panel to the web page.
- Fields: education, graduation year, major, target roles, adjacent roles, target companies, target cities, and excluded roles.
- Privacy: session-only mode does not write to the database; saved mode stores structured fields only and discards `raw_resume` and `resume_text`.
- Verification: profile save/delete and session-only behavior passed; full test suite is 10/10.

### RUN-M001-001 / Explicit hard conditions with full-job preservation

- Date: 2026-08-15
- Status: Completed
- Implementation: added `/api/jobs/with-profile`; explicit excluded roles receive `hard_filter_pass=false` and explainable reasons, while remaining available in the all-jobs response.
- Verification: exclusion and city preference cases passed in the API test suite.

### RUN-M002-001 / Explainable four-pool recommendations

- Date: 2026-08-15
- Status: Completed
- Implementation: added `/api/recommendations` and a web button; deterministic pools are main, target company, adjacent, and exploration with 50/25/20/5 default quotas.
- Verification: pool labels, target-company reasons, and quota strategy passed; full test suite is 12/12.
- Boundary: this is rule-based ranking, not a claim of AI accuracy or admission probability.

### RUN-M003-001 / Adjacent explanations and competition risk

- Date: 2026-08-15
- Status: Completed
- Implementation: recommendation items now include adjacent-role explanations, competition risk level, and public-signal basis.
- Boundary: risk is an estimate based on job text only; no admission probability is produced.
- Verification: adjacent explanation and risk evidence tests passed; full test suite is 12/12.

### RUN-U001-001 / Search and recommendation workspace

- Date: 2026-08-15
- Status: Completed
- Implementation: connected search, profile-based recommendations, explanations, favorites, and official application links in the web workspace.
- Added actions: favorite, ignore, and applied are supported by the action API; the first UI control is favorite.
- Verification: favorite toggle, profile, recommendation, source registry, and snapshot endpoints passed; full test suite is 13/13.
- Boundary: the recommendation engine remains deterministic and explainable; AI resume parsing and automated application are not enabled.

### RUN-P002-001 / Resume preview and structured candidate extraction

- Date: 2026-08-15
- Status: Pending feedback
- Implementation: added `/api/resume/preview` and a web file preview flow for PDF/DOCX; added standard-library DOCX XML and common PDF text-stream extraction.
- Output: education, graduation-year candidates, skills, text-length evidence, and explicit user-confirmation flag. Job-seeking intent remains separate and empty by default.
- Privacy: original file and extracted text are returned only for the current request; no raw resume is written to SQLite.
- Verification: PDF preview, DOCX extraction, unsupported-format rejection, and full suite passed; 16/16 tests.
- Boundary: external AI analysis is not enabled yet; the extracted profile is only a candidate preview until user confirmation.

### RUN-P002-002 / Configurable AI profile provider

- Date: 2026-08-15
- Status: Completed
- Implementation: added `/api/resume/analyze` with local-rules default and optional OpenAI-compatible provider controlled by `AI_PROFILE_PROVIDER`, `AI_BASE_URL`, `AI_API_KEY`, and `AI_MODEL`.
- Privacy gate: external provider calls require `external_ai_consent=true`; missing configuration fails closed; raw resume is never persisted.
- Verification: local provider endpoint test passed; full suite is 21/21 after subsequent additions.

### RUN-TAXONOMY-001 / Unified job families

- Date: 2026-08-15
- Status: Completed
- Implementation: added job-family taxonomy, confidence, and evidence fields with non-destructive migration and backfill.
- Result: 509 of 520 jobs classified; 11 remain unknown rather than guessed.
- Verification: algorithm and sales classification tests passed; job-family facet and filtering are available.

### RUN-COMPLIANCE-001 / Low-frequency source controls

- Date: 2026-08-15
- Status: Completed
- Implementation: same-source crawl cooldown defaults to 3600 seconds; ingestion queue exposes only reachable, non-excluded sources ordered by priority.
- Verification: cooldown and queue exclusion tests passed; no live crawl was run in this unit.

### RUN-D003-001 / Beisen-compatible adapter

- Date: 2026-08-15
- Status: Pending feedback
- Scope: implement a reusable parser for Beisen/Zhiye-style campus job JSON.
- Implementation: added `crawler/beisen_jobs.py`; connected `beisen_jobs_browser` mode in `crawler/runner.py`.
- Fields: job ID, title, city, recruitment type, category, degree, description, requirements, published time, and detail URL.
- Verification: two local fixtures representing 360-style and Beisen-style payloads; duplicate positions are removed; 6/6 unit tests passed.
- Boundary: no recruitment website access and no live crawl execution in this unit.
- Conclusion: parser layer is complete; live 360/Beisen acceptance remains the next controlled step.

### RUN-U001-002 / Feedback state and saved-job views

- Date: 2026-08-15
- Status: Completed
- Implementation: added action-state hydration on page load; favorite, ignore, and applied controls are toggleable; added tabs for all jobs, favorites, ignored, and applied jobs.
- API: `GET /api/job-actions` now supports `?action=favorite|ignore|applied` with validation.
- Verification: endpoint filter assertion added; browser smoke check found 4 view tabs, 100 rendered job cards, and 60 source rows after reload; full unittest suite is 21/21.
- Boundary: actions are local MVP state; no automatic application or external message is sent.

### RUN-INTEGRATION-001 / Initial product integration acceptance

- Date: 2026-08-15
- Status: Completed
- Scope: verify the current first-version chain from source registry and job database through API and web workspace.
- Baseline: 520 total job rows, 513 active jobs, 7 crawl runs, 52 companies, 60 deduplicated career sources.
- Verification: `/health` returned 200; `/api/facets` returned 513 active jobs; browser reload showed source registry, profile panel, filters, recommendation entry, and feedback tabs; `node --check static/app.js`, Python compilation, and `unittest discover` 21/21 passed.
- Data protection: the job table was not rewritten by this integration unit; an independent SQLite fingerprint was recorded as `aa11fda2342611bd83edfc413fb7557ed5b71763a186ac80f42b930595d81ba7` for the 520-row baseline; no live bulk crawl was run.
- Remaining controlled work: live 360/Beisen single-source acceptance, real Luna endpoint configuration, 11 unknown job families, and future semantic retrieval/evaluation.

### RUN-P002-003 / Resume confirmation into capability profile

- Date: 2026-08-15
- Status: Completed
- Implementation: added a separate skills evidence field and a user-confirmation action that transfers only education, candidate graduation-year evidence, and extracted skills into the editable capability profile.
- Boundary: target roles, adjacent roles, target companies, cities, and exclusions are never populated from the resume; the user must set those intent fields separately.
- Verification: profile-save tests already accept structured skills; browser smoke check found the skills field and confirmation control; no raw resume is persisted.

### RUN-M004-001 / Full matching dimensions and feedback soft preference

- Date: 2026-08-15
- Status: Completed
- Implementation: recommendation items now expose basic qualification, ability match, job-seeking intent, company preference, transition distance, evidence confidence, and feedback actions as separate dimensions. Explicit ignore is a soft preference that removes a job from recommendation pools while preserving it in all-job search.
- Verification: recommendation dimension assertions and ignore-preservation test passed; full unittest suite is 25/25.
- Boundary: no hard condition is inferred from resume evidence, no admission probability is generated, and sales volume does not create a recommendation bonus.

### RUN-COMPLIANCE-002 / Generic discovery stop gates

- Date: 2026-08-15
- Status: Completed
- Implementation: generic browser JSON discovery now stops on HTTP 403/429 and common CAPTCHA/security-verification markers; the crawler applies a concrete-position quality gate before mutating the job table.
- Verification: blocked-signal, navigation-card rejection, and quality-gate tests passed; Python compilation passed.
- Live check: one 360 and one 北森 public source were contacted sequentially. The captured payloads contained navigation cards but no qualified concrete positions under the quality gate; the two run records were corrected to failed/protected and the 12 invalid rows were removed. No bulk retry was performed.

### RUN-AUDIT-001 / Current full baseline

- Date: 2026-08-15
- Status: Completed
- Verification: 520 total job rows, 507 active jobs, 6 quarantined rows, 9 recorded crawl runs including the two protected live attempts; `/api/job-quality` reports zero missing active required fields; `node --check static/app.js`; Python compilation; unittest suite 30/30; local `/health` 200; browser showed 4 feedback tabs, 100 all-job cards, and 100 recommendation explanation summaries after reload.
- Remaining product decisions/evidence: configure a real Luna endpoint for external-model acceptance, manually label an evaluation set for ranking quality, and wait for controlled source cooldown before any further live attempt.

### RUN-DATA-QUALITY-001 / Quarantine non-job Envision records

- Date: 2026-08-15
- Status: Completed
- Finding: six historical `envision-campus` rows were privacy-policy, recruitment-plan/graduate-cohort navigation, or empty-detail records rather than concrete applyable positions.
- Action: retained the rows and their raw evidence, changed only their status to `quarantined`; they are excluded by the normal active-job query and remain auditable.
- Verification: `/api/job-quality` reports 520 total, 507 active, 6 quarantined, and zero missing active required fields; all 30 tests pass.
- Boundary: no valid Xiaomi/Xiaopeng job rows were changed; no records were deleted.

### RUN-EVAL-001 / Offline recommendation evaluation set

- Date: 2026-08-15
- Status: Completed
- Scope: synthetic, non-network cases covering algorithm-versus-sales volume, user-selected target company, high competition, missing graduation year, explicit sales exclusion, and ignored-job soft feedback.
- Artifact: `EVALUATION_CASES.md` and `tests/test_recommendation_eval.py`.
- Verification: five executable high-risk cases passed as part of the 30-test suite; no admission probability is calculated.

### RUN-P002-004 / External AI consent and fail-closed verification

- Date: 2026-08-15
- Status: Completed
- Implementation: documented all AI provider variables in `.env.example`; external provider requests require explicit consent and return a configuration error when endpoint, key, or model is absent.
- Verification: consent-denied and missing-configuration tests passed; full unittest suite is now 31/31.
- Boundary: no external model was contacted and no API key was invented.

### RUN-FINAL-001 / Final implementation audit

- Date: 2026-08-15
- Status: Completed
- Current evidence: 520 total rows, 507 active, 6 quarantined; 31/31 tests; JavaScript syntax check; Python compilation; `/health` 200; `/api/job-quality` reports zero missing active required fields; browser shows 4 feedback views and recommendation explanations.
- Documentation: final implementation addendum is in `LUNA_IMPLEMENTATION_SPEC.md`; source-of-truth execution history remains this file.
- Explicit external boundary: real Luna credentials/model endpoint were not supplied; 360/北森 live payloads failed the concrete-position gate and were protected without retrying inside the cooldown window.

### RUN-UX-001 / Three-layer workspace explanation

- Date: 2026-08-15
- Status: Completed
- Finding: source registry, user profile, and job workspace were visually adjacent but had different audiences and responsibilities, causing user confusion.
- Implementation: added purpose banners, a three-step resume/profile guide, separate visual headings for capability evidence and job-seeking intent, and `USAGE_GUIDE.md`.
- Verification: browser reload showed all three purpose banners, two profile group labels, 100 job cards, and no console errors; `node --check static/app.js` passed.

### PLAN-V02-001 / V0.2 产品化实施方案

- 日期：2026-08-15
- 状态：已通过
- 目标：将现有功能集合收敛为用户可理解、Luna 可连续实施和验收的 V0.2 产品方案。
- 当前证据基线：520 条岗位记录、507 条活动岗位、6 条隔离记录、52 家企业、60 条去重入口、9 条运行记录、31/31 unittest 通过。
- 方案产出：新增 `PRODUCT_V0_2_IMPLEMENTATION_PLAN.md`；将 `LUNA_IMPLEMENTATION_SPEC.md` 更新为当前唯一执行规格；同步 `DEVELOPMENT_OUTLINE.md`、`GATE_ANALYSIS.md`、`README.md` 和本 Harness 的当前状态。
- 执行顺序：UX-002 → UX-003 → P-003 → M-005 → P-004 → D-006 → OPS-001 → R-002。
- 第一单元：UX-002 前后台与画像拆分，建立 `/`、`/profile`、`/admin/sources` 三个职责清晰的页面。
- 外部边界：本次只编写实施方案，未访问招聘官网、未运行采集、未调用外部 AI、未修改数据库和岗位数据。
- 结论：方案可直接交给 Luna 实施；没有外部卡口时按单元连续推进，每次保留运行记录和验收证据。

### RUN-UX-002-001 / 前后台与画像页面拆分

- 日期：2026-08-15
- 状态：已通过
- 开始基线：520 总岗位、507 活动、6 隔离、52 企业、60 入口、9 运行、31 测试。
- 修改文件：`app/main.py`、`static/index.html`、`static/profile.html`、`static/admin-sources.html`、`static/app.js`、`static/profile.js`、`static/admin-sources.js`、`static/styles.css`、`tests/test_pages.py`。
- 产出：新增 `/profile` 和 `/admin/sources`；首页仅保留岗位工作台；后台展示来源、队列、质量和运行状态；画像功能迁移到独立页面。
- 自动验证：页面路由与职责测试通过；JavaScript 语法检查通过；随后全套测试通过。
- 浏览器验证：首页导航和岗位卡可见；页面职责由 DOM 回归测试确认。因本地服务旧进程占用，重启验证过程中服务生命周期不稳定，已通过 HTTP 页面回归补充确认。
- 外部访问：无招聘官网访问、无外部 AI。
- 结论：UX-002 通过，进入 UX-003。

### RUN-UX-003-001 / 完整岗位分页与详情访问

- 日期：2026-08-15
- 状态：已通过
- 范围：兼容式扩展 `/api/jobs`，新增 `offset` 元数据响应和岗位页“加载更多”。
- 修改文件：`app/db.py`、`app/main.py`、`static/index.html`、`static/app.js`、`static/styles.css`、`tests/test_pagination.py`。
- 验收：旧调用仍返回数组；带 `offset` 返回 `items/total/offset/limit`；分页无重复，过滤总数正确；详情继续显示地点、招聘类型、描述、要求和官方链接。
- 自动验证：全套 unittest 34/34（本单元完成时）通过；JavaScript/Python 检查通过。
- 数据保护：生产库基线仍为 520 总岗位、507 活动、6 隔离、9 运行。
- 外部访问：无招聘官网访问。
- 结论：UX-003 通过，进入 P-003。

### RUN-P-003-001 / 画像引导与确认闭环

- 日期：2026-08-15
- 状态：已通过
- 范围：画像页明确能力证据/求职意愿边界，增加城市偏好/硬限制和推荐组合比例。
- 修改文件：`static/profile.html`、`static/profile.js`、`app/db.py`、`tests/test_profile.py`。
- 验收：简历仍需用户确认后才写入；城市默认为软偏好，选择硬限制才影响硬过滤；推荐比例必须合计 100%；保存结构化字段不保存原始简历。
- 自动验证：全套 unittest 36/36（本单元完成时）通过。
- 外部访问：无招聘官网访问、无外部 AI。
- 结论：P-003 通过，进入 M-005。

### RUN-M-005-001 / 推荐离线评测与排序校准

- 日期：2026-08-15
- 状态：已通过
- 范围：将离线推荐评测从 6 个基础场景扩展为 30 个可执行变体。
- 修改文件：`EVALUATION_CASES.md`、`tests/test_recommendation_eval.py`。
- 覆盖：销售数量偏置、目标企业召回、算法竞争风险、毕业年份缺失、明确排除销售、解释完整性，每类 5 个案例。
- 自动验证：全套 unittest 37/37（本单元完成时）通过；最终页面拆分测试加入后为 38/38。
- 发布卡口：无硬条件误杀、目标企业独立召回、销售不因数量进入主攻、推荐包含六个匹配维度和召回通道。
- 外部访问：无招聘官网访问、无外部 AI。
- 结论：M-005 通过；暂不引入未经评测的语义黑盒排序，进入 P-004/D-006 分支。

### RUN-P-004-001 / 真实 Luna 结构化分析验收

- 日期：2026-08-15
- 状态：被阻塞
- 已完成检查：本地规则 provider、外部同意门、缺配置失败关闭测试均通过；当前全套测试 38/38。
- 阻塞原因：未提供 `AI_BASE_URL`、`AI_API_KEY`、`AI_MODEL`，不能调用真实 Luna/OpenAI-compatible 端点，也不能伪造外部模型结果。
- 继续条件：提供兼容端点、模型名、密钥，并确认使用脱敏/合成简历样本；密钥不写入仓库或 Harness。

### RUN-D-006-001 / 新企业具体岗位扩展

- 日期：2026-08-15
- 状态：被阻塞
- 已完成检查：接入队列可排序，飞书/北森解析器和具体岗位质量门槛已有本地 fixture；现有 360、北森真实小样本曾被质量门槛保护。
- 阻塞原因：当前没有同时满足“新来源官方归属已确认、公开访问合规、冷却窗口已通过”的可安全重试来源；远景保持隔离，360/北森不在冷却窗口内重复访问。
- 继续条件：冷却窗口结束且选定单个已授权来源后，再一次性小样本验证；403、429、验证码或登录墙立即停止。

### RUN-OPS-001-001 / 可控更新与采集锁

- 日期：2026-08-15
- 状态：已通过
- 范围：采集请求改为后台任务返回；新增 SQLite 来源锁和 `python -m crawler.worker --source <id>` 单来源 worker。
- 修改文件：`app/db.py`、`app/main.py`、`crawler/worker.py`、`tests/test_worker.py`。
- 行为：同一来源不能并发运行；锁可释放，过期锁可恢复；API 请求不等待采集完成；冷却、质量门槛和停止信号仍由现有 runner 执行。
- 自动验证：全套 unittest 40/40；Python 编译和 JavaScript 语法检查通过。
- 外部访问：本单元未运行 worker，未访问招聘官网。
- 结论：OPS-001 通过；D-006 仍等待外部来源卡口，R-002 可进行非外部回归。

### RUN-R-002-001 / V0.2 非外部发布回归

- 日期：2026-08-15
- 状态：待反馈
- 验收链路：`/` 搜索岗位 → `/profile` 保存画像与推荐比例 → `/api/recommendations` 四类推荐 → 收藏/忽略/已投递 → `/admin/sources` 查看数据质量和运行记录。
- 数据完整性：分页遍历 `/api/jobs?offset=&limit=100` 得到 507 条活动岗位，唯一 ID 507，无重复；数据库仍为 520 总记录、507 活动、6 隔离、52 企业、60 入口、9 运行。
- 页面验证：三个路由均 200；首页只显示岗位工作台；画像页显示能力证据、求职意愿和推荐比例；管理页显示入口、接入队列、岗位质量和运行记录；浏览器三页回归无控制台错误。
- 自动验证：全套 unittest 39/39；JavaScript 语法检查和 Python 编译检查通过；活动岗位必需字段缺失数为 0。
- 外部边界：未调用真实 Luna；未访问新招聘官网；D-006/P-004 仍是外部阻塞项。
- 结论：V0.2 本地产品链路达到待反馈，不能将外部 AI 验收和新企业岗位覆盖描述为已完成。

### RUN-V02-AUDIT-002 / 当前最终审计

- 日期：2026-08-15
- 状态：待反馈
- 当前基线：520 总岗位、507 活动岗位、6 隔离、52 企业、60 去重入口、10 次采集运行、40/40 unittest。
- UX-002/UX-003/P-003/M-005/OPS-001：已通过；三页浏览器回归无控制台错误；507 条岗位分页遍历无重复。
- P-004：仍被阻塞，仅完成外部同意门、缺配置失败关闭和模型输出结构校验；没有真实 Luna 端点，因此没有真实模型结果。
- D-006：仍未通过，360 冷却后重验仍无合格具体岗位，蔚来入口此前超时，远景保持隔离。
- 外部访问：本次审计未访问招聘官网，未调用外部 AI。
- 结论：当前本地 V0.2 产品可查看；完整外部数据覆盖和真实 Luna 验收需要解除上述两个外部条件。

### RUN-D-006-002 / 蔚来 Feishu 单来源公开入口检查

- 日期：2026-08-15
- 状态：需修改
- 范围：对接入队列中的蔚来 Feishu 校招入口进行一次公开页面检查，未启动岗位写入。
- 结果：页面加载阶段超时，未获得可验证的具体岗位列表；未发现可用于通过质量门槛的岗位数据。
- 保护动作：未重试、未绕过访问控制、未写入 `jobs`、未改变现有岗位状态；该来源保持待分析。
- 外部访问：仅一次公开入口检查；无登录、验证码处理或并发请求。
- 结论：D-006 仍未通过。后续需要新的官方可访问来源或冷却结束后的单来源受控验收，不能把本次超时当成成功采集。

### RUN-D-006-003 / 360 北森小样本冷却后重验

- 日期：2026-08-15
- 状态：需修改
- 输入：已确认官方的 `https://360campus.zhiye.com/jobs`，单来源、最多 5 条小样本、无重试。
- 结果：`crawl_produced_no_qualified_concrete_jobs`；发现 0 条通过具体岗位字段门槛的记录，新增 0，岗位表未改变。
- 数据保护：运行记录增加 1 条失败记录，数据库仍为 520 总岗位、507 活动、6 隔离；失败快照受保护。
- 外部边界：只访问该单一公开入口；未绕过验证码、登录墙或访问控制；未继续重试。
- 结论：360 当前解析链路仍需修改或等待可验证的具体岗位接口；D-006 继续保持未通过。
