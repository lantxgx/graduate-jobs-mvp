# AI 批量企业校招录入标准操作文档

## 目标

根据 `data/company-onboarding-roster.json` 逐家公司处理。名单是唯一任务队列，状态必须原地更新：`待录入` → `录入中` → `录入成功`、`失败` 或 `部分失败`。

## 每家公司执行步骤

1. 读取企业名称、`official_url`、当前 `status`。跳过 `录入成功`；`失败` 和 `部分失败` 只在有新证据时重试。
2. 如果 `official_url` 为空，搜索企业官网并进入“校园招聘/应届生/实习生”入口。只保存企业官方页面，不保存聚合站、公众号文章或搜索结果页；把最终 URL 写回 `official_url`，并把 `url_status` 改为 `已验证`。
3. 正常打开页面，确认没有登录墙、验证码、403、429 或安全验证。遇到这些情况，写 `失败` 和 `failed_reason`，不得绕过。
4. 判断采集方式：有稳定公开 JSON/API 且可取得详情，标记 `method=自动`；只有页面可见岗位、接口不稳定或字段无法稳定解析，标记 `method=手动`。
5. 将状态改为 `录入中`，再采集 3–20 条具体岗位作为首批样本。自动方式必须记录接口 URL、分页参数和总数；手动方式必须从官方详情页逐条复制。
6. 每条岗位必须使用统一字段：`company`、`title`、`country`、`province`、`city`、`category`、`major`、`job_nature`、`degree`、`graduate_year`、`requirements`、`description`、`apply_url`、`source_url`、`source_job_id`、`published_at`。
7. 不得推断学历、专业、城市、招聘类型或截止日期。官网缺失就留空并记录字段缺口；但质量门禁要求的字段缺失时，该条进入隔离区，不得作为成功岗位。
8. 自动采集全部岗位且分页闭合：`录入成功`；只采到部分岗位但至少有合格岗位：`部分失败`，`success_jobs` 填成功数、`failed_reason` 写未完成原因；完全没有合格岗位：`失败`。
9. 每家公司写维护任务文件 `source-maintenance/tasks/SRC-YYYYMMDD-<source-id>.md`，保留官方 URL、接口证据、岗位数量、拒绝原因和运行命令。
10. 执行标准校验并刷新 `data/standardized/companies-all.json`、`docs/jobs.json`。没有通过校验不得把状态写成 `录入成功`。

## 自动与手动的选择规则

| 条件 | 方式 |
|---|---|
| 官方页面正常加载产生公开岗位 API，详情 URL 稳定 | 自动 |
| 公开分页接口可访问，但详情字段需要浏览器渲染 | 自动适配器 + 浏览器详情 |
| 页面只有可见岗位卡片，接口不稳定或签名随时变化 | 手动 |
| 登录、验证码、403、429、安全验证 | 失败，不能绕过 |
| 只有招聘公告，没有具体岗位详情 | 失败，不能入库 |

## 手动录入

开发者打开 `/admin/manual`，逐条填写官方页面中的原文，然后提交。页面调用 `POST /api/manual/jobs`，接口和自动采集使用同一套字段规范、标准化函数和质量门禁。接口拒绝缺字段、非 HTTP 官方 URL、未知招聘类型和没有职责/要求的记录。

## 状态更新示例

```json
{
  "company": "示例企业",
  "official_url": "https://example.com/campus",
  "url_status": "已验证",
  "method": "手动",
  "status": "部分失败",
  "success_jobs": 7,
  "failed_reason": "详情页中 3 条缺少学历要求"
}
```
