# 国内企业校招录入名单与方法

这份名单是新增来源的执行队列。URL 必须先打开并确认属于企业官方招聘入口，再按“自动 / 手动”方式处理；不能从搜索摘要或第三方聚合页直接写岗位。

| 企业 | 官方校招 URL | 方式 | 当前状态 |
|---|---|---|---|
| 海康威视 | https://campushr.hikvision.com/school?schoolType=nozxf&activeTab=0 | 自动：公开岗位 API | 已接入 20 条 |
| 腾讯云智 | https://app-tc.mokahr.com/campus-recruitment/csig/20001 | 自动：Moka jobs/module + 详情页 | 已接入 2 条 |
| 哔哩哔哩 | https://jobs.bilibili.com/campus/positions?type=1 | 自动候选：公开 positionList API | 待适配 |
| 科大讯飞 | https://campus.iflytek.com/official-pc/jobList | 手动候选：北森/自建混合页面 | 待人工确认 |
| 快手 | https://campus.kuaishou.cn | 手动候选：动态页面 | 待人工确认 |
| 小红书 | https://job.xiaohongshu.com/campus/position | 自动候选：公开 pageQueryPosition API | 待适配 |
| 华为 | https://career.huawei.com/reccampportal/portal5/campus-recruitment.html | 手动候选 | 待人工确认 |
| 蚂蚁集团 | https://talent.antgroup.com/campus-full-list?type=campus_graduates | 手动候选 | 待人工确认 |
| 京东 | https://campus.jd.com | 自动：公开岗位分页接口 | 已接入 |
| 美团 | https://zhaopin.meituan.com/web/campus | 自动：公开岗位接口 | 已接入 |
| 拼多多 | https://careers.pddglobalhr.com/campus/grad | 自动：公开岗位接口 | 已接入 |
| 小米 | https://xiaomi.jobs.f.mioffice.cn/internship/ | 自动：飞书接口 | 已接入 |
| 小鹏汽车 | https://xiaopeng.jobs.feishu.cn/campus/position/list | 自动：飞书接口 | 已接入 |
| OPPO | https://careers.oppo.com/university/oppo/campus/post | 自动：公开岗位接口 | 已接入 |
| 米哈游 | https://jobs.mihoyo.com/#/campus/position | 自动：公开岗位接口 | 已接入 |
| 联想 | https://talent.lenovo.com.cn | 自动：公开岗位接口 | 已接入 |
| 北森 | https://beisen.zhiye.com | 自动：北森分页接口 | 已接入 |
| 网易游戏 | https://game.campus.163.com/position | 手动候选 | 待人工确认 |
| 绿盟科技 | https://campus.nsfocus.com | 手动候选 | 待人工确认 |
| 理想汽车 | https://www.lixiang.com/employ/social/list.html | 手动候选 | 待人工确认 |

## 统一录入流程

1. 打开官方 URL，记录页面标题、最终 URL、是否公开可访问。
2. 自动来源：只调用页面正常加载产生的公开接口，先采 3～20 条，再核对分页总数。
3. 手动来源：打开岗位详情，逐条复制原文，不补写缺失字段；每条岗位都必须有官方详情/投递 URL。
4. 使用统一字段：`company`、`title`、`country`、`province`、`city`、`category`、`major`、`job_nature`、`degree`、`graduate_year`、`requirements`、`description`、`apply_url`、`source_url`、`source_job_id`、`published_at`。
5. 手动录入接口：`POST /api/manual/jobs`，请求体为 `{ "jobs": [ ... ] }`。缺字段、非官方 URL、无法识别招聘类型或没有职责/要求的记录会被拒绝。
6. 成功后运行标准导出和校验，前端只读 SQLite/`docs/jobs.json`，不维护第二套字段。

示例：

```json
{"jobs":[{"company":"示例企业","title":"算法工程师","city":"中国 / 浙江省 / 杭州市","category":"算法/AI","degree":"硕士","job_nature":"全职","requirements":"计算机、数学等相关专业","description":"负责算法研发。","apply_url":"https://example.com/job/123","source_url":"https://example.com/campus","source_job_id":"123"}]}
```
