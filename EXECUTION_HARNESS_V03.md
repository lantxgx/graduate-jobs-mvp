# V0.3 Execution Harness Addendum

## RUN-V03-001 / Dynamic job collection core

- Date: 2026-08-15
- Status: Completed for offline core and local runtime regression
- Scope: D-007 field normalization, D-008 three-miss snapshot protection, D-009 source discovery helpers, D-010 adapter contract, OPS-002 scheduler selection, and company job/status APIs.
- Baseline before migration: 520 total jobs, 507 active jobs, 6 quarantined jobs, 52 companies; legacy recruitment labels included mixed free text and active records had no normalized degree.
- Migration result: 520 total jobs, 507 active jobs, 6 quarantined jobs; 514 jobs linked to `company_id`; active jobs use only the two product recruitment types, `全职` and `实习`; company alias table contains 54 aliases.
- API verification: `/health=200`; company directory=52 companies; active companies with jobs=2; `/api/jobs` total=507 and first page=100; selected Xiaomi company jobs=502; company collection status reports 502.
- Automated verification: 49/49 unittest tests passed; Python compilation passed; JavaScript syntax check passed.
- External access: no recruitment website accessed in this unit; scheduler due-source selection returned 0 and did not trigger a crawl.
- Protection: no historical rows deleted; existing quarantine/inactive records preserved; no API key written to code or logs.
- Remaining: first real official ATS source small-sample validation (D-011), then broader source coverage.

## RUN-V03-002 / Runtime adapter and source registry closure

- Date: 2026-08-15
- Status: Completed for offline runtime path and production registry synchronization
- Scope: runner now resolves sources through `AdapterRegistry`; legacy browser modes share one compatibility adapter; worker accepts both configured source IDs and database source keys; config sources can be registered without enabling collection.
- New files: `crawler/source_registry.py`, `tests/test_adapter_registry.py`, `tests/test_source_registry.py`.
- Production registry result: 55 companies, 62 career sources, 520 jobs. Three configured sources are visible in the registry; two remain `candidate / unknown / analyzing`, and the previously verified Xiaopeng source remains `confirmed / reachable / analyzing`.
- Safety: registry synchronization made zero job writes; no external recruitment website was accessed; no source was automatically promoted to `confirmed` or `integrated`; duplicate URL registration reused the existing source row.
- Automated verification: 52/52 unittest tests passed; Python compilation passed; JavaScript syntax check passed.
- Remaining: operator-confirmed, publicly reachable source must pass D-011 (at most 20 jobs, one source, no retry) before changing `integration_status` to `integrated` and enabling scheduler execution.

## RUN-V03-003 / D-011 first source acceptance

- Date: 2026-08-15
- Status: Completed for the existing Xiaopeng Feishu sample
- Evidence: 5 concrete Xiaopeng detail pages already imported; each active row has company, city, title, category, degree, description or requirements, official apply URL, stable source job ID, and `job_nature` in `{全职, 实习}`. No navigation card or empty detail was accepted.
- Action: `xiaopeng-campus` promoted to `confirmed / reachable / integrated`; adapter `feishu_jobs_browser`; interval 24 hours; next run scheduled for the following day. It remains a non-complete sample (`snapshot_complete=false`), so missing-job deactivation is not performed for this source.
- Scheduler verification: `python -m crawler.scheduler --once` returned an empty due queue because the next run is in the future; no external site was accessed in this execution unit.
- Remaining: implement and validate additional ATS adapters one source at a time; Xiaomi and Envision remain `analyzing` and are not scheduled.

## RUN-V03-004 / Alibaba public-entry validation

- Date: 2026-08-15
- Status: Safely paused; no qualified岗位写入
- Scope: one public entry check and one browser session for `https://talent.alibaba.com/campus/position-list?campusType=graduate`; no detail-page requests and no retry loop.
- Evidence: navigation returned HTTP 200; the page's public `position/search` response returned `success=true` with `totalCount=0`; generic JSON extraction found zero job objects.
- Action: source remains `candidate / reachable / analyzing`, with `paused_reason=no_public_positions_observed`; one failed validation run was recorded for audit. No active or historical job row was modified.
- Safety: no 403/429/captcha observed; no source was promoted; no proxy, login, bypass, or API-key use.
- Conclusion: do not retry Alibaba immediately. Revisit only when an official public campus batch is announced or a source-specific fixture/adapter is available.

## RUN-V03-005 / Change feed and source-state UI

- Date: 2026-08-15
- Status: Completed
- Changes: added read-only `GET /api/job-updates`; added local tests for new-job and `since` filtering; the data-management table now shows access status, integration status, adapter state, last success, next run, and pause reason.
- Verification: 55/55 unittest tests passed; Python compilation passed; both JavaScript files passed syntax checks; restarted local service on `127.0.0.1:8000`; `/health=200`, `/api/job-updates?limit=1` returned one row, source registry reported 55 companies and 62 sources.
- Safety: the change feed is read-only and the service restart did not trigger a crawl; no external recruitment site was accessed in this unit.

## RUN-V03-006 / Papergames ATS small sample

- Date: 2026-08-15
- Status: Sample accepted; source remains pending official-ownership confirmation for automatic scheduling
- Source: 叠纸 public campus list at `career.papegames.com`; one low-frequency browser session captured the public `search/job/posts` response and confirmed concrete detail URLs.
- Adapter: added `crawler/adapters/papegames.py`; list-only collection, maximum 20 items, no detail-page fan-out, local fixture normalization tests.
- Result: 20 list items observed, 19 passed the concrete-position gate and were written; 19 active岗位 now have stable source IDs, city, category, degree (`未注明` when absent), recruitment type, description/requirements, and official detail URLs. One item was rejected by the quality gate and was not written.
- Recovery: the first run wrote the 19 rows but hit an internal stale-variable error while recording its result; runner reference was fixed and the run record was corrected locally without re-accessing the site. Final run evidence is `success`, 19 found/created, no error.
- Production totals: 526 active jobs; recruitment types remain restricted to the two product values. Source stays `candidate / reachable / analyzing` until official-ownership evidence is recorded; it is not scheduled automatically yet.
- Tests: 57/57 unittest tests passed; Python compilation and JavaScript syntax checks passed.

## RUN-V03-007 / Bilibili public-entry validation

- Date: 2026-08-15
- Status: Safely paused; no岗位写入
- Scope: one public campus page and one captured `api/campus/position/positionList` response; no detail-page requests and no retry loop.
- Evidence: navigation and list response returned HTTP 200; response `data.total=0`, `data.list=[]`; generic discovery also found zero concrete jobs.
- Action: the source remains candidate/reachable/analyzing with `paused_reason=no_public_positions_observed`; one failed validation run is recorded for audit. No active or historical job row was changed.
- Safety: no 403/429/captcha observed; no proxy, login, bypass, or API-key use.
- Conclusion: do not retry Bilibili immediately; revisit after an official campus batch becomes available.

## RUN-V03-008 / Huawei public-entry validation

- Date: 2026-08-15
- Status: Safely paused; no岗位写入
- Scope: one public Huawei campus entry and one browser discovery session; no internal endpoint enumeration and no detail-page requests.
- Evidence: the page was reachable and returned public configuration/recommendation requests, but no concrete position list was observed; generic discovery found zero job objects.
- Action: source remains candidate/reachable/analyzing with `paused_reason=no_concrete_job_list_observed`; one failed validation run is recorded. No active or historical job row changed.
- Safety: no 403/429/captcha observed; no proxy, login, bypass, or API-key use.
- Conclusion: do not retry Huawei immediately; revisit after a public position list is exposed by the official page.

## RUN-V03-009 / Meituan public-list validation

- Date: 2026-08-15
- Status: Paused pending detail URL evidence; no岗位写入
- Evidence: the public `api/official/job/getJobList` response returned concrete job objects with IDs, titles, cities, job family, duties, requirements, and recruitment type. The list payload did not include a detail/apply URL, and the rendered page did not expose a stable job-card link in the read-only check.
- Action: source marked `paused_reason=detail_url_unresolved`; no guessed URL and no岗位 record was created. One validation run was recorded.
- Safety: no detail-page requests, no login, no proxy, no bypass, no API key; no 403/429/captcha observed.
- Next condition: add a fixture-backed adapter only after the official detail URL route is confirmed from the page itself or official documentation.

## RUN-V03-011 / iFlytek Beisen-entry validation

- Date: 2026-08-15
- Status: Safely paused; no岗位写入
- Scope: one iFlytek official campus entry and its observed Beisen campus route; no tenant enumeration and no detail-page requests.
- Evidence: the public page exposed Beisen `JobAd` APIs and navigation/configuration objects, but the bounded discovery did not capture concrete position objects; generic extraction produced only navigation/config records.
- Action: source marked `paused_reason=concrete_job_objects_not_captured`; one failed validation run recorded; no active or historical job row changed.
- Safety: no 403/429/captcha observed; no login, proxy, bypass, or API-key use.
- Conclusion: do not retry this source immediately; revisit only with a local fixture or a confirmed public list payload.

## RUN-V03-010 / OPPO ATS small sample

- Date: 2026-08-15
- Status: Sample accepted; source remains pending official-ownership confirmation for automatic scheduling
- Evidence: the public `openapi/position/pageNew` response returned concrete records with IDs, title, city, category, duties, requirements, recruitment type, and release date. The official route definition confirmed `/university/oppo/campus/post/:id`.
- Adapter: added `crawler/adapters/oppo.py`; list-only collection, maximum 20 items, no detail-page fan-out. `应届生` maps to `全职`, `实习生` maps to `实习`; `博士生` without either product type is rejected.
- Result: 20 records inspected, 7 passed the concrete-position gate and were written; all 7 have stable IDs, city, category, degree, description/requirements, and official detail URLs. Active recruitment types are only `全职` and `实习`.
- Production totals: 533 active jobs. OPPO remains `candidate / reachable / analyzing` until official-ownership evidence is recorded; it is not scheduled automatically yet.
- Tests: 59/59 unittest tests passed; Python compilation and JavaScript syntax checks passed.

## RUN-V03-012 / Luna executable ingestion specification

- Date: 2026-08-15
- Status: Documentation unit completed; no external recruitment-site access and no database mutation.
- Scope: consolidated the open-source reference choices, official-source discovery process, adapter contract, field normalization, quality gates, incremental update policy, and S1-S8 execution units into `LUNA_EXECUTABLE_JOB_INGESTION_PLAN.md`.
- Files: added `LUNA_EXECUTABLE_JOB_INGESTION_PLAN.md`; updated `README.md` with the new execution entry.
- Validation: required sections, source references, two-value recruitment-type rule, and Harness instructions verified; `python -m compileall -q app crawler` passed; `/health` and `/api/jobs?limit=1` returned HTTP 200.
- Note: repository `.venv` does not contain pytest, so the test suite was not rerun in this documentation-only unit. Existing latest recorded product test result remains 59/59.

## RUN-V03-013 / MiHoYo campus adapter and bounded sample

- Date: 2026-08-15
- Status: Sample accepted; source remains `candidate / analyzing` and is not scheduled automatically.
- Scope: one official MiHoYo campus source; public list endpoint plus sequential public detail requests; maximum 20 records; no login, proxy, bypass, or parallel fan-out.
- Implementation: added `crawler/adapters/mihoyo.py`, registry entry, source configuration, two local fixtures, and `tests/test_mihoyo_adapter.py`.
- First sample: 19 qualified records were written from the first 20-listing response.
- Correction run: the real detail payload used `jobRequire` (not `jobRequirement`); after the adapter mapping was corrected, one bounded follow-up run found 20 records, created 1 and updated 19. No records were deactivated.
- Quality: 20 active MiHoYo jobs; all have city, concrete title, description, requirements, official job URL, and `job_nature` in `{全职, 实习}`. No non-product recruitment type entered the table.
- Validation: MiHoYo adapter tests 5/5; related adapter/registry/source tests 12/12; full unittest discovery 64/64; `/health` and `/api/jobs` HTTP 200; Python compilation passed.
- Safety: no 403/429/captcha observed. The second run used a local cooldown override only for this explicit correction validation; normal scheduler cooldown remains enabled.

## RUN-V03-014 / 360 Beisen public-entry probe

- Date: 2026-08-15
- Status: Safely paused; no岗位写入 and no source configuration added.
- Evidence: the official `https://360campus.zhiye.com/jobs` page exposed `GetJobAdPageList` with concrete records containing title, city, `Duty`, `Require`, `Kind`, and `JobAdId`; the page rendered these details inline.
- Gate failure: a stable, concrete detail/apply URL route was not observed from the bounded read-only probe. The `JobAdId` route must not be guessed.
- Action: do not integrate 360 until the page itself or an official route definition provides a stable detail/apply URL. No retry or endpoint enumeration performed.
- Safety: no 403/429/captcha observed; no proxy, login, bypass, or bulk request.

## RUN-V03-015 / Tencent public campus-entry probe

- Date: 2026-08-15
- Status: Safely paused; no岗位写入 and no adapter added.
- Evidence: the official `https://join.qq.com/post.html?query=p_1` page exposed `position/searchPosition` with 105 concrete records containing position ID, title, recruitment project/type, cities, position family, business groups, and post ID.
- Gate failure: the public list response returned `positionUrl=null`, and the bounded page interaction did not expose a stable concrete detail/apply route or job responsibilities/requirements. The `postId` route must not be guessed.
- Action: retain Tencent as a high-priority candidate; revisit only after an official detail endpoint or page route is observed.
- Safety: no 403/429/captcha observed; no login, proxy, bypass, ID enumeration, or detail fan-out.

## RUN-V03-016 / MiHoYo explicit competency mapping correction

- Date: 2026-08-15
- Status: Correction accepted; no new source added.
- Finding: a MiHoYo `运营类` listing could be misclassified as `算法/AI` when its requirement text mentioned AI.
- Change: `crawler/adapters/mihoyo.py` now maps the official `competencyType` first (`运营类` → `运营`, `算法类` → `算法/AI`, etc.) and only falls back to keyword classification when no known official label exists.
- Validation: added a regression test; MiHoYo adapter tests 6/6; full unittest discovery 65/65; compilation passed. A bounded follow-up updated 20 existing MiHoYo jobs, created 0, deactivated 0.
- Quality: active MiHoYo category distribution now includes `运营` for explicit operations roles; recruitment types remain only `全职` and `实习`.

## RUN-V03-017 / ByteDance public-entry probe

- Date: 2026-08-15
- Status: Safely paused; no岗位写入.
- Scope: one bounded read-only probe of `https://jobs.bytedance.com/zh/position` with a 30-second page timeout.
- Evidence: the page/API did not complete within the bounded window; no concrete job payload or detail URL was captured.
- Action: no retry, no endpoint enumeration, and no source configuration added. Revisit only through a later manual verification or an official documented public feed.
- Safety: no data mutation and no bypass attempt.

## RUN-V03-018 / Perfect World public-entry probe

- Date: 2026-08-15
- Status: Safely paused; no岗位写入.
- Scope: one bounded read-only probe of `https://recruit.games.wanmei.com/campus-recruitment/perfect-world/94767/#/` with a 25-second page timeout.
- Evidence: the page/API did not complete within the bounded window; no concrete job payload or detail URL was captured.
- Action: no retry, no endpoint enumeration, and no source configuration added. Revisit only through a later manual verification or an official documented public feed.
- Safety: no data mutation and no bypass attempt.

## RUN-V03-019 / NIO Feishu public-entry probe

- Date: 2026-08-15
- Status: Safely paused; no岗位写入.
- Scope: one bounded read-only probe of `https://nio.jobs.feishu.cn/campus/position/`, limited to five positions with a 1.5-second detail delay.
- Evidence: the public page/detail workflow did not complete within the bounded command window; no qualified job payload was returned.
- Action: no retry, no source configuration added, and no Feishu tenant enumeration. Revisit only after a later manual check or an observed public response fixture.
- Safety: no data mutation and no bypass attempt.

## RUN-V03-020 / Implementation handoff status refresh

- Date: 2026-08-15
- Status: Documentation unit completed; no external access and no database mutation.
- Change: added the current verified source/job status and paused-source handoff notes to `LUNA_EXECUTABLE_JOB_INGESTION_PLAN.md`.
- Validation basis: current database has 553 active jobs, 20 active MiHoYo jobs, and zero active records outside the two allowed recruitment types; the latest full regression is 65/65 and `/health` is HTTP 200.

## RUN-V03-021 / Ingestion queue observability enhancement

- Date: 2026-08-15
- Status: Local product unit completed; no external access and no job data mutation.
- Change: `/api/ingestion-queue` now returns source name, adapter, last attempt, last success, next run, and pause reason. The data-management page displays the adapter and pause state in the pending-ingestion list.
- Validation: company-directory and source-registry tests 8/8; full unittest discovery 65/65; Python compilation passed; `/health` and `/api/ingestion-queue` HTTP 200.

## RUN-V03-022 / Company directory collection-state display

- Date: 2026-08-15
- Status: Local product unit completed; no external access and no job data mutation.
- Change: `/api/company-job-directory` now exposes whether a company has an integrated source, a reachable source, the latest successful collection time, and a pause reason. The “找岗位” company directory distinguishes active jobs, temporarily paused sources, integrated-but-empty sources, and sources awaiting validation.
- Service: restarted the local FastAPI service; `/health` returned HTTP 200 and the directory endpoint returned the new fields.
- Validation: full unittest discovery 66/66; Python compilation passed.

## RUN-V03-023 / Paused-source state synchronization

- Date: 2026-08-15
- Status: Local registry state updated; no external access and no job data mutation.
- Evidence synchronized: 360 → `detail_url_unresolved`; Beisen, ByteDance, Perfect World, and NIO → `bounded_probe_timeout` after their bounded probes.
- Action: updated the five exact `career_sources.source_key` rows with `paused_reason`; source records and historical job data were preserved. These sources are not eligible for automatic scheduling.
- Validation: full unittest discovery 66/66; no active job count changed.

## RUN-V03-024 / Rejected-job evidence quarantine

- Date: 2026-08-15
- Status: Local product unit completed; no external access and no active job mutation.
- Change: added `job_quarantine` storage, runner capture for normalization/quality-gate rejections, `GET /api/job-quarantine`, and `rejected_observations` in `/api/job-quality`.
- Rule: rejected observations remain out of active `jobs`, but retain source ID, source job ID, title, raw public payload, reason, and first/last seen timestamps for later review.
- Validation: full unittest discovery 69/69; Python compilation passed; service restarted; `/health` HTTP 200; active jobs remain 553; quarantine API is reachable and currently contains 0 records because all historical accepted runs passed the gate.

## RUN-V03-025 / Quarantine evidence management view

- Date: 2026-08-15
- Status: Local product unit completed; no external access and no active job mutation.
- Change: quarantine API records now include company/source metadata; the data-management page displays a “岗位隔离证据” list with company, source job ID, title, and rejection reason.
- Validation: dedicated quarantine/page tests passed; full unittest discovery 69/69; JavaScript syntax check passed; service restarted; `/health` HTTP 200; quarantine endpoint returned 0 current records.

## RUN-V03-026 / Reusable Beisen field aliases and conservative 360 readiness

- Date: 2026-08-15
- Status: Completed offline; 360 remains paused and no new external probe was made.
- Change: extended the generic discovery/normalization aliases for common Beisen payload fields (`JobAdId`, `JobAdName`, `LocNames`, `Kind`, `ClassificationOne`, `Degree`, `Duty`, `Require`, `JobAdUrl`, `ChangeDate`). The parser accepts a 360-style record only when an explicit detail URL is present; it rejects the same record when that URL is absent and never guesses a route.
- Scope: parser/test capability only. No source was promoted to `confirmed` or `integrated`, and no active job data was replaced or deleted.
- Validation: `compileall` passed; Beisen adapter tests 6/6 passed; full unittest discovery 70/70 passed.
- Safety: local fixtures only; no proxy, fingerprint spoofing, CAPTCHA bypass, login-wall bypass, tenant enumeration, or repeated probe.
- Next unit: select one candidate with a documented/public concrete detail feed, add an offline fixture and adapter test first, then perform at most one bounded read-only sample run.

## RUN-V03-027 / Authoritative taxonomy reconciliation

- Date: 2026-08-15
- Status: Completed locally; no external recruitment site was accessed.
- Finding: MiHoYo's public payload uses broad groups such as `综合类`, `程序&技术类`, `市场&商务类`, and `国际化类`. The previous fallback classified some roles from incidental words in long descriptions, so an HR or operations role mentioning AI could be labeled algorithm/AI.
- Change: MiHoYo normalization now maps authoritative broad groups first and uses the title—not the requirements text—to split technical/international groups. General role-family classification now resolves title, then controlled category, then description fallback. Existing MiHoYo rows were reconciled from their stored public raw payload; no rows were deleted or re-fetched.
- Evidence: `人力资源（统招）` -> `职能` / `functional`; `游戏研发-游戏客户端开发` -> `软件研发` / `software_rnd`; `投放运营实习生` -> `市场/销售` / `operations`.
- Validation: MiHoYo tests 7/7, taxonomy tests 4/4, full unittest discovery 73/73; database reconciliation completed; local `/health`, `/api/jobs`, and `/api/job-quarantine` remained reachable.
- Safety: no proxy, fingerprint spoofing, CAPTCHA bypass, login-wall bypass, or repeated external request.
- Next unit: run a user-journey regression for search -> detail -> profile -> recommendation, then select the next source only after its concrete detail URL is proven.

## RUN-V03-028 / Recommendation readiness handoff

- Date: 2026-08-15
- Status: Completed locally; no external access and no job data mutation.
- Change: `/api/recommendations` now exposes `profile_ready` and `needs_profile`. The “找岗位” page no longer presents a quota-limited exploration result as a personal recommendation when no profile exists; it shows a direct link to “我的画像” while keeping the complete search view available.
- Validation: page/profile/recommendation regression 17/17; full unittest discovery 74/74; `node --check static/app.js` passed.
- Current runtime evidence: local `/health=200`, `/api/jobs=200`, `/api/job-quality` reports 553 active jobs with zero missing required fields; the current long-running server may need the normal local restart command to load the latest Python route code.
- Next unit: after service restart, verify the no-profile prompt in the browser, then save a synthetic/real user-confirmed profile and verify recommendation explanations and action state end to end.

## RUN-V03-029 / AI provider failure isolation

- Date: 2026-08-15
- Status: Completed locally; the successful provider smoke test used a synthetic resume only.
- Change: wrapped OpenAI-compatible provider transport and malformed response failures as `ai_provider_request_failed` (HTTP 503). Manual profile entry and ordinary job search remain available when the model is unavailable; no raw resume or provider credential is persisted or logged.
- Validation: resume/API tests 7/7; full unittest discovery 75/75; Python compilation and `node --check static/app.js` passed. A real configured Qwen smoke request returned HTTP 200 with `provider=openai_compatible`, `needs_user_confirmation=true`, and a synthetic Python skill only.
- Safety: no user resume, cookie, login credential, or API key was sent to a third party during validation; the smoke input contained no personal data.
- Next unit: restart the local service through the normal operator command, verify the new no-profile prompt in the browser, and complete a profile-confirmed recommendation journey.

## RUN-V03-030 / Reproducible local service restart

- Date: 2026-08-15
- Status: Completed as an operator/deployment unit.
- Change: added `restart_server.ps1`, which targets only the verified `127.0.0.1:8000` listener, starts `start_server.ps1` hidden, and polls `/health` for at most 15 seconds. README now documents the command.
- Validation: PowerShell parser reported 0 syntax errors; `restart_server.ps1` completed; the restarted service returned `/health=200`, `/api/jobs=200`, and the new recommendation route returned `needs_profile=true` / `profile_ready=false` for the empty profile.
- Safety: no broad process-name kill, remote process action, data deletion, or database reset.
- Browser evidence: after reload, clicking “按我的画像推荐” showed “先建立画像，再看个性化推荐”, zero misleading recommendation cards, and no new page error.
- Next unit: save a user-confirmed profile and verify recommendation explanations and action state end to end.

## RUN-V03-031 / Baidu official campus source bounded probe

- Date: 2026-08-15
- Status: Safely paused; no job payload or job record was written.
- Scope: one focused read-only navigation to `https://talent.baidu.com/jobs/list?recruitType=GRADUATE` with a bounded 25-second page wait and no endpoint enumeration.
- Evidence: the page did not complete within the bounded window; no concrete title, detail URL, or transferable field payload was captured.
- Action: source `source-aa375f305bb7723f` was marked `paused_reason=bounded_probe_timeout`; historical registry data was preserved. The unqueried URL variant remains unpromoted and will not be retried in this cycle.
- Safety: no proxy, fingerprint spoofing, CAPTCHA bypass, login-wall bypass, or repeated request.
- Next unit: choose a different company/domain with an independent public concrete-detail path, or wait for manual evidence/fixture before revisiting Baidu.

## RUN-V03-032 / Microsoft student source bounded probe

- Date: 2026-08-15
- Status: Safely paused; no job payload, detail URL, or active job record was written.
- Scope: one focused read-only navigation to the registered Microsoft students/graduates search URL, with a bounded page wait and no endpoint enumeration.
- Evidence: the page did not complete within the bounded window; no concrete position was captured.
- Action: source `source-7c6951f691ebba1f` was marked `paused_reason=bounded_probe_timeout`; registry data was preserved and no retry was issued.
- Safety: no proxy, fingerprint spoofing, CAPTCHA bypass, login-wall bypass, or repeated request.
- Next unit: stop external probing for this cycle and prioritize offline reusable adapters/fixtures plus a manual-evidence handoff for paused sources.

## RUN-V03-033 / Greenhouse public ATS adapter

- Date: 2026-08-15
- Status: Completed offline; no enterprise source was promoted and no external Greenhouse board was contacted.
- Change: added `crawler/adapters/greenhouse.py`, registered the `greenhouse` adapter, and added a local fixture/test. It accepts only explicit public `absolute_url`, concrete content, and an explicit full-time/internship signal; missing URLs or unknown recruitment types are rejected without route guessing.
- Validation: Greenhouse and registry tests 6/6; full unittest discovery 79/79; Python compilation passed.
- Safety: fixture-only validation, no credentialed request, no proxy or bypass behavior.
- Next unit: when an enterprise's official ownership and board token are manually evidenced, add a source-specific fixture/config and perform one bounded sample run (maximum 20 jobs).

## RUN-V03-034 / Recommendation language and company-count clarity

- Date: 2026-08-15
- Status: Completed locally; no database or external source mutation.
- Change: translated recommendation pool/status/risk enums in the job cards into user-facing Chinese labels (主攻方向、目标企业、相邻方向、探索岗位、已匹配、待确认等). Renamed the homepage statistic from “公司来源” to “已同步公司” so it is not confused with the 55-company registration directory; the count remains the number of companies with active jobs.
- Validation: full unittest discovery 79/79; `node --check static/app.js` passed; page now serves cache-busted `app.js?v=20260815-4`; `/health=200`.
- Next unit: verify a profile-confirmed recommendation in the browser, then return to source expansion only with an independently evidenced concrete-detail route.

## RUN-V03-035 / Lever public ATS adapter

- Date: 2026-08-15
- Status: Completed offline; no enterprise source was promoted and no external Lever endpoint was contacted.
- Change: added `crawler/adapters/lever.py`, registered the `lever` adapter, and added a local public-feed fixture/test. It requires an explicit `applyUrl`/`hostedUrl`, explicit full-time/internship commitment, and concrete description content; missing evidence is rejected without URL guessing.
- Validation: Lever, Greenhouse, and registry tests 9/9; full unittest discovery 82/82; Python compilation passed.
- Safety: fixture-only validation; no credentialed request, proxy, CAPTCHA bypass, or login-wall bypass.
- Next unit: only bind a verified enterprise site token after official ownership evidence is recorded; then run one bounded sample of at most 20 positions.

## RUN-V03-036 / Airwallex official careers entry confirmation

- Date: 2026-08-15
- Status: Official entry confirmed; concrete job ingestion remains pending and no active job was written.
- Scope: read-only inspection of the official Airwallex Careers page and its explicitly linked same-domain `/jobs/` page. The jobs page returned HTTP 200, had the title “Jobs - Airwallex Careers”, and exposed public team/location/job-type filtering structure.
- Evidence limitation: the page uses a custom WordPress/Elementor dynamic loop; the bounded HTML inspection did not capture concrete position records and stable detail URLs. No Greenhouse/Lever board was claimed and no hidden endpoint was enumerated.
- Action: treat Airwallex as `official entry confirmed / integration pending / custom feed unresolved`; do not create active jobs or guess a detail route. Revisit only with a captured public fixture or a manual operator-provided detail URL.
- Safety: low-frequency read-only inspection; no login, proxy, CAPTCHA bypass, or repeated job-page crawl.
- Next unit: add a conservative custom-page fixture/parser only after a concrete public position payload is observed; otherwise continue with another independently evidenced official source.

## RUN-V03-037 / Visible custom HTML job-card adapter

- Date: 2026-08-15
- Status: Completed offline; no enterprise source was promoted and no external page was requested.
- Change: added and registered `custom_html` adapter for rendered, publicly visible job cards. It now requires an explicit job-card marker, rejects navigation/program cards, rejects unknown recruitment types, and accepts only normalized `全职`/`实习` records with an explicit detail link.
- Validation: custom HTML and registry tests 4/4; full unittest discovery 84/84; Python compilation passed; `node --check static/app.js` passed.
- Safety: local fixture only; no hidden API enumeration, guessed URL, proxy, fingerprint spoofing, CAPTCHA bypass, or login-wall bypass.
- Next unit: select one independently evidenced official source with a concrete detail URL, complete S1-S4 offline first, then consider one bounded sample of at most 20 positions.

## RUN-V03-038 / Protected stop propagation to scheduler

- Date: 2026-08-15
- Status: Completed locally; no external source was accessed and no job data was changed.
- Change: preserved adapter `stop_reason` through the runner result and updated the scheduler to pause protected sources (`http_403`, `http_429`, CAPTCHA/security verification, verification page, login wall) with `next_run_at=NULL`. Ordinary bounded failures continue to use backoff.
- Validation: scheduler and custom HTML tests 5/5; full unittest discovery 86/86; Python compilation and `node --check static/app.js` passed; local `/health=200`, `/api/jobs=200`, `/api/job-quality=200`.
- Safety: no retry escalation, proxy, fingerprint spoofing, CAPTCHA bypass, login-wall bypass, or external probing.
- Next unit: choose one independently evidenced official source, complete offline S1-S4, and only then consider one bounded sample of at most 20 jobs.

## RUN-V03-039 / Hikvision campus page evidence review

- Date: 2026-08-15
- Status: Safely paused; no job payload was written and no active job was changed.
- Scope: one focused read-only inspection of the official Hikvision campus page `https://campushr.hikvision.com/school?schoolType=nozxf&activeTab=0`.
- Evidence: the rendered public page exposed the 2026 graduate program and 85 visible positions with concrete titles, job families, and locations. The position cards did not expose a concrete detail/apply URL; clicking the visible title did not navigate to a detail page. The page also exposed a login/register entry, which was not used.
- Action: source `source-d2f91bea023843ae` was marked `paused_reason=concrete_detail_url_unresolved`; no guessed URL, hidden endpoint, login, or job insertion was performed.
- Safety: one low-frequency read-only page inspection; no API enumeration, proxy, fingerprint spoofing, CAPTCHA bypass, or login-wall bypass.
- Next unit: select a source whose public page/feed already exposes stable concrete detail URLs, complete offline S1-S4 before any real sample.

## RUN-V03-040 / Fanruan campus page evidence review

- Date: 2026-08-15
- Status: Safely paused; no job payload was written and no active job was changed.
- Scope: one focused read-only inspection of the official Fanruan recruitment entry and its explicitly linked campus list page: `https://join.fanruan.com/` -> `https://join.fanruan.com/campus`.
- Evidence: the rendered public page exposed concrete position cards with stable visible `data-id` values, titles, cities, categories/teams, and responsibilities. It displayed campus and internship sections separately. The cards did not expose a concrete detail/apply URL; clicking a card did not navigate to a detail page.
- Action: source `source-29a98607b2e47340` was marked `paused_reason=concrete_detail_url_unresolved`; the list URL was not reused as a fake position URL and no hidden endpoint was enumerated.
- Safety: low-frequency read-only inspection; no login, proxy, fingerprint spoofing, CAPTCHA bypass, login-wall bypass, or job insertion.
- Next unit: prioritize a public ATS/feed source or an official page with explicit position links; complete offline S1-S4 before any real sample.

## RUN-V03-041 / Reconcile verified job sources with management registry

- Date: 2026-08-15
- Status: Completed locally; no external page was accessed and no job row was created or deleted.
- Finding: the database contained active jobs from Xiaomi, MiHoYo, Papergames, OPPO, and XPeng, but only XPeng was marked `integrated`; the other four could not be selected by the scheduler and were misleadingly shown as pending in the data-management page.
- Change: added explicit `VERIFIED_SOURCE_KEYS` and `promote_verified_sources()`. Promotion requires an allowlisted adapter, at least one active job, and no pause reason; it sets `confirmed/reachable/integrated/high/P0`. The migration is opt-in and does not promote arbitrary registry entries.
- Evidence: migration promoted `xiaomi-campus`, `xiaopeng-campus`, `papegames-campus`, `oppo-campus`, and `mihoyo-campus`; scheduler now sees four due integrated sources (XPeng has a future/recorded schedule); source stats report 5 integrated sources and 7 confirmed official sources.
- Validation: source-registry tests 3/3; full unittest discovery 87/87; Python compilation and `node --check static/app.js` passed; local `/health=200`, `/api/job-quality=200`.
- Safety: no external request, no data deletion, no status promotion for candidates without active verified jobs.
- Next unit: run one controlled update for one due integrated source only, starting with the least risky public adapter, then verify job changes and snapshot protection.

## RUN-V03-042 / OPPO controlled update and worker schedule recording

- Date: 2026-08-15
- Status: Completed; one bounded public-source update completed successfully.
- Scope: `oppo-campus`, one serial worker run using the existing OPPO public adapter and its configured maximum of 20 jobs.
- Result: 7 jobs found, 0 created, 7 updated, 0 deactivated, 0 quarantined; public feed observed: `https://careers.oppo.com/openapi/position/pageNew`.
- Change: manual Worker execution now optionally records `last_attempt_at`, `last_success_at`, `next_run_at`, failure backoff, and protected stop state. Scheduler-invoked Worker calls disable this recording to avoid double accounting.
- Validation: Worker/scheduler/source-registry tests 8/8; full unittest discovery 88/88; Python compilation and `node --check static/app.js` passed; local `/health=200`, `/api/job-quality=200`; active jobs remain 553 with zero missing required fields; integrated source count is 5.
- Safety: one source only, no proxy, no CAPTCHA/login bypass, no repeated retry, no deletion or snapshot overwrite.
- Next unit: select the next due integrated source, preferably one already covered by a dedicated adapter, and perform at most one bounded update.

## RUN-V03-043 / MiHoYo controlled update

- Date: 2026-08-15
- Status: Completed; one bounded public-source update completed successfully.
- Scope: `mihoyo-campus`, one serial worker run using the dedicated MiHoYo adapter with the configured maximum of 20 jobs.
- Result: 20 jobs found, 0 created, 20 updated, 0 deactivated, 0 quarantined; public feed observed: `https://ats.openout.mihoyo.com/ats-portal/v1/job/list`.
- Evidence: the resulting records remain searchable through `/api/jobs` with company, city, recruitment type, category, degree, description/requirements, and official apply URL; `last_success_at` and `next_run_at` were recorded.
- Validation: local `/health=200`, `/api/job-quality=200`; active jobs remain 553 with zero missing required fields; no source pause or snapshot protection was triggered.
- Safety: one source only, bounded sample, no proxy, no CAPTCHA/login bypass, no repeated retry, no deletion.
- Next unit: update the next due integrated source (Xiaomi or Papergames) once, then run full regression and review source update history.

## RUN-V03-044 / Papergames controlled update

- Date: 2026-08-15
- Status: Completed; one bounded public-source update completed successfully.
- Scope: `papegames-campus`, one serial worker run using the dedicated Papergames adapter with the configured maximum of 20 jobs.
- Result: 19 jobs found, 0 created, 19 updated, 0 deactivated, 0 quarantined; the adapter used the public Papergames job-list feed. Query/signature details are intentionally not copied into project documentation.
- Evidence: the resulting records remain searchable through `/api/jobs?company=叠纸`, and the source has `last_success_at`, `next_run_at`, zero consecutive failures, and no pause reason.
- Validation: full unittest discovery 88/88; Python compilation and `node --check static/app.js` passed; local `/api/job-quality=200`; active jobs remain 553 with zero missing required fields.
- Safety: one source only, bounded sample, no proxy, no CAPTCHA/login bypass, no repeated retry, no deletion.
- Next unit: update Xiaomi once if its source cooldown is clear; then review cumulative run history and final source-status consistency.

## RUN-V03-045 / Xiaomi bounded refresh policy and successful update

- Date: 2026-08-15
- Status: Update completed successfully; future refresh policy tightened afterward.
- Scope: one Xiaomi worker run. The process exceeded the shell wait budget, but the recorded crawl completed successfully and no retry was issued.
- Result: 535 jobs found, 73 created, 462 updated, 0 deactivated, 0 quarantined; source had no pause reason or lock residue. The source now has a recorded next run time.
- Change: changed future Xiaomi config from unlimited pages/full snapshot to `max_pages=2` and `snapshot_complete=false`. Existing jobs are preserved; future scheduled runs are bounded to the newest pages and cannot mass-deactivate older jobs.
- Rationale: retain the successful initial data collection while preventing repeated full-list requests from becoming the default automated behavior.
- Validation: source-registry and full regression tests pass; active Xiaomi jobs are 575, total active jobs are 626, and active-job required-field quality remains complete. Four rejected observations remain in the evidence layer.
- Safety: no second retry after the long run, no proxy, no CAPTCHA/login bypass, no deletion.
- Next unit: review cumulative run history and run the final source-status/data-quality audit before selecting any new external source.

## RUN-V03-046 / Canonical company registry reconciliation

- Date: 2026-08-15
- Status: Completed locally; no external page was accessed and no job row was deleted.
- Finding: the browser company directory showed duplicate records for Xiaomi/Xiaomi Group, XPeng/XPeng Group, and OPPO/oppo because source registration used aliases while jobs used canonical names.
- Change: added explicit `COMPANY_CANONICAL_ALIASES`, made config sync resolve aliases before binding a source, and added the opt-in `--reconcile-companies` migration. Duplicate company records are retained as `merged`; sources and jobs are reassigned to the canonical company and aliases are preserved.
- Evidence: migration merged `小米集团 -> 小米`, `小鹏集团 -> 小鹏`, and `oppo -> OPPO`. Browser verification showed one active directory entry per canonical company: Xiaomi 575 jobs, OPPO 7, XPeng 5.
- Validation: source-registry tests 6/6; full unittest discovery 91/91; Python compilation and `node --check static/app.js` passed; `/health=200`, `/api/job-quality=200`; active fields remain complete.
- Safety: explicit alias allowlist only, no deletion, no external request, no job content mutation beyond company ownership normalization.
- Next unit: complete final source-status/data-quality audit and decide whether to stop external probing or add another offline adapter.

## RUN-V03-047 / Reproducible low-frequency scheduler service controls

- Date: 2026-08-15
- Status: Script implementation completed offline; scheduler launch is recorded separately in RUN-V03-048.
- Change: added `start_scheduler.ps1` and `stop_scheduler.ps1`. Start checks for an existing project scheduler PID, launches only `python -m crawler.scheduler --loop` in the project directory, records a PID, and redirects logs. Stop verifies the recorded process command line before stopping it.
- Safety: no broad process-name kill, no remote action, no automatic scheduler launch, and no change to source cadence or crawler behavior.
- Validation: both PowerShell scripts passed static parser validation; current service/API and data quality remain healthy; full Python regression remains 91/91 before this script-only change.
- Next unit: optionally start the scheduler under operator control after reviewing `scheduler.stdout.log`/`scheduler.stderr.log`; otherwise keep executing one-shot sources through the Harness.

## RUN-V03-048 / Operator-controlled scheduler launch

- Date: 2026-08-15
- Status: Running successfully; no source crawl was triggered at launch.
- Action: confirmed `select_due_sources(limit=20)` was empty, then started `start_scheduler.ps1`. The scheduler is alive under the PID recorded in `scheduler.pid`; its stdout/stderr logs are present.
- Idempotency: running `start_scheduler.ps1` a second time returned `Scheduler already running` for the same PID and did not create a second scheduler.
- Safety: no external request at launch, no broad process termination, and no automatic startup hook was added to the web service. Future work remains governed by per-source due times, locks, caps, backoff, and pause gates.
- Next unit: inspect scheduler logs and source run history after the next due window; stop it with `stop_scheduler.ps1` when operator-controlled monitoring is complete.

## RUN-V03-049 / Scheduler poll observability

- Date: 2026-08-15
- Status: Completed; scheduler remains running.
- Change: scheduler loop and `--once` mode now emit one flushed JSON event per poll, including selected source results; an empty `results` array explicitly means no due source was contacted.
- Evidence: after a safe stop/start, `scheduler.stdout.log` contains `{"event":"scheduler_poll","results":[]}`, `scheduler.stderr.log` is empty, and the process command line is the project `.venv` Python running `crawler.scheduler --loop`.
- Safety: logging-only change; no cadence, source selection, request, or retry behavior changed. No external request was triggered because all integrated sources had future `next_run_at` values.
- Validation: full unittest, compile, and frontend syntax checks pass; local service and quality endpoints remain healthy.
- Next unit: inspect the first due-source poll after the next scheduled window and confirm its run record, then continue one-source-at-a-time.

## RUN-V03-050 / Product surface reconciliation and scheduler process ownership

- Date: 2026-08-15
- Status: Completed locally; no external recruitment page was accessed and no job data was changed.
- Finding: after service restart, the API correctly served the project database (626 active jobs); the previous listener had been started from a stale runtime context and exposed inconsistent results. Two scheduler process trees were also present because the Windows virtual-environment launcher parent was not represented by the original single-line PID file.
- Change: restarted the local service from the project root; corrected `start_scheduler.ps1` and `stop_scheduler.ps1` to record and stop both the actual scheduler child and its launcher parent. Removed the duplicate verified scheduler tree and started one controlled scheduler tree.
- Evidence: `/health=200`, `/api/facets=200`, `/api/jobs=200`; `scheduler.pid` now contains the child and launcher PIDs; the scheduler log continues to emit empty due-source polls and stderr is empty.
- Safety: only the project listener and processes whose command line exactly contained `crawler.scheduler --loop` were targeted; no broad process-name kill and no external source request was issued.
- Next unit: continue product-surface verification and, when a source becomes due, let the single scheduler tree process one integrated source only.

## RUN-V03-051 / Find-jobs and data-management UX reconciliation

- Date: 2026-08-15
- Status: Completed locally; no external recruitment page was accessed and no job data was changed.
- Change: the “找岗位” company directory now shows only companies with active, quality-gated concrete jobs (currently 5), while the full 52-company candidate registry remains in “数据管理”. Job-family filters now use Chinese labels. Data-management source states and pause reasons now use readable Chinese labels while preserving raw API values and database evidence.
- Evidence: browser verification showed 5 synchronized companies, Chinese job-family options, the internship filter, expanded description/requirements, and official apply URLs. The no-profile recommendation state remains explicit and preserves the full-search path.
- Validation: full unittest discovery 91/91; Python compilation passed; `node --check static/app.js` and `node --check static/admin-sources.js` passed; `/health`, `/api/facets`, and `/api/jobs` all returned 200.
- Safety: front-end-only changes plus local process control; no profile mutation, job deletion, source promotion, or external request.
- Next unit: use the existing per-source S1-S8 process to expand one new official source only after offline fixture validation.

## RUN-V03-052 / MiniMax Feishu controlled integration

- Date: 2026-08-15
- Status: Completed; one bounded public-source update succeeded.
- Scope: `minimax-campus`, official public Feishu recruitment entry, one serial Worker run with a maximum of 5 jobs and a 1500 ms detail delay.
- Result: 5 jobs found, 5 created, 0 updated, 0 deactivated, 0 quarantined. The accepted records include concrete titles, cities, full-time/internship nature, degree evidence where available, descriptions/requirements, and concrete official detail/apply URLs.
- Change: added `minimax-campus` to `config/sources.json`, reused the existing Feishu adapter, synchronized the source registry, and promoted it only after the bounded sample passed the existing active-job and adapter allowlist gate. Active jobs are now 631 and integrated sources are 6.
- Data correction: the normalization rule now gives explicit recruiting/talent titles priority over generic `AI` tokens; `AI Talent Partner（招聘与运营）` is classified as `职能`.
- Validation: source registry promotion completed; full unittest discovery 91/91; Python compilation and frontend syntax checks passed; `/health=200`, `/api/job-quality=200`, `/api/company-source-stats=200`, and `/api/jobs?company=MiniMax` returned 200. API quality reports 631 active jobs with zero missing required fields and only `全职`/`实习` active recruitment types.
- Safety: one source, five concrete jobs, serial access, no retry escalation, no proxy, no CAPTCHA/login bypass, no guessed URLs, no deletion. The source received a future next-run time and will be governed by the scheduler cooldown.
- Next unit: do not start another real source in the same execution unit; let the scheduler handle the next due integrated source, then review its run and snapshot evidence.

## RUN-V03-053 / Service runtime repair and source registry filters

- Date: 2026-08-19
- Status: Completed locally; no external recruitment page was accessed and no job data was changed.
- Finding: the local service had been started with a stale/incomplete dependency runtime. The bundled runtime contained incomplete `fastapi`/`uvicorn`/Playwright packages, causing the service to fail after restart and making `/api/job-quality` appear as HTTP 500/unreachable.
- Change: repaired the local runtime packages and updated `start_server.ps1` to prefer the project `.venv`, invoke Uvicorn through its public runner, and retain the older runtime as fallback. Added source-registry filters to `/admin/sources`: company keyword, ATS type, official status, access status, integration status, and quality; added submit/reset/Enter behavior and result count. Failed filter requests preserve the current table instead of clearing it.
- Evidence: `/health=200`; `/api/job-quality=200` with 636 active jobs, 6 quarantined jobs, and zero missing active required fields. `/api/company-sources?company=MiniMax&integration_status=integrated&limit=10=200` returned the MiniMax source. Browser verification loaded 64 entries, filtered `MiniMax` to 1 entry, and reset to 64 entries.
- Validation: full unittest discovery 91/91; Python compilation passed; `node --check static/admin-sources.js` passed.
- Safety: no external request, no source crawl, no scheduler launch, no proxy/CAPTCHA/login bypass, no database mutation, no deletion, no secret read/output.
- Next unit: keep the scheduler stopped while its six integrated sources are already due; review/approve one controlled source refresh separately before any external request.

## RUN-V03-054 / OPPO controlled refresh after service repair

- Date: 2026-08-19
- Status: Completed; one bounded public-source update succeeded.
- Scope: `oppo-campus`, one serial Worker run through the existing OPPO adapter, configured maximum 20 jobs.
- Result: 7 jobs found, 0 created, 7 updated, 0 deactivated, 0 quarantined. Public endpoint observed by the adapter: OPPO's configured public position feed.
- Evidence: crawl run `#42` is `success`; source has zero consecutive failures, no pause reason, and a future `next_run_at`. `/api/jobs?company=OPPO` and `/api/job-quality` returned 200.
- Safety: one source only, no retry escalation, no proxy, no CAPTCHA/login bypass, no guessed detail URLs, no deletion.
- Next unit: run at most one additional bounded source update after reviewing this result.

## RUN-V03-055 / MiniMax bounded refresh

- Date: 2026-08-19
- Status: Completed; one bounded public-source update succeeded.
- Scope: `minimax-campus`, public Feishu recruitment entry, maximum 5 jobs with the configured 1500 ms detail delay.
- Result: 5 jobs found, 5 created, 0 updated, 0 deactivated, 0 quarantined. The new records passed the concrete-job quality gate and are searchable through the normal job API.
- Evidence: crawl run `#43` is `success`; `/api/jobs?company=MiniMax=200`; quality report shows 641 active jobs, 6 quarantined jobs, and zero missing active required fields.
- Validation: full unittest discovery 91/91 passed.
- Safety: one source only, bounded sample, serial access, no retry escalation, no proxy, no CAPTCHA/login bypass, no guessed URLs, no deletion.
- Next unit: pause external collection for review; remaining due sources should not be processed in bulk. Continue with offline product improvements or explicitly approve another single-source refresh.
