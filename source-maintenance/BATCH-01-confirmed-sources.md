# 批次 01：已登记且已有岗位结果的招聘源

这些来源已经在 `config/sources.json` 中登记，数据库中也有历史成功记录。维护任务是“低频增量更新”和“发现字段质量问题”，不是重新高频全量抓取。

| source id | 公司 | 招聘官网/入口 | 当前适配器 | 数据库历史状态 |
|---|---|---|---|---|
| `xiaomi-campus` | 小米集团 | https://xiaomi.jobs.f.mioffice.cn/internship/ | `xiaomi_jobs_browser` | 已有大量实习岗位 |
| `xiaopeng-campus` | 小鹏集团 | https://xiaopeng.jobs.feishu.cn/campus/position/list | `feishu_jobs_browser` | 已有少量岗位 |
| `papegames-campus` | 叠纸 | https://career.papegames.com/campus/position/list | `papegames` | 已有岗位 |
| `oppo-campus` | OPPO | https://careers.oppo.com/university/oppo/campus/post | `oppo` | 已有岗位 |
| `mihoyo-campus` | 米哈游 | https://jobs.mihoyo.com/#/campus/position | `mihoyo` | 已有岗位 |
| `minimax-campus` | MiniMax | https://vrfi1sk8a0.jobs.feishu.cn/s/i6nd8qwp | `feishu_jobs_browser` | 已有岗位 |
| `envision-campus` | 远景科技集团 | https://envision-career.com/campus-recruitment/envisiongroup/43123/#/jobs | `browser_json` | 历史上存在页面质量问题，需人工复核 |

## 单来源运行

在仓库根目录执行，命令一次只跑一个来源：

```powershell
& .\.venv\Scripts\python.exe -m crawler.worker --source xiaopeng-campus
```

也可以使用：

```powershell
& .\.venv\Scripts\python.exe -m crawler.runner --source xiaopeng-campus
```

看到 `http_403`、`http_429`、`verification_page_detected` 或 `no_concrete_visible_job_cards` 时，不要重复运行；把结果写入任务模板并等待人工处理。

## 字段核验重点

- `title`：具体岗位名称，不是“校园招聘”“招聘计划”。
- `city`：岗位页面明确给出的工作城市；多城市应按项目现有规范保存，不能自行猜测。
- `job_nature`：只能为 `全职` 或 `实习`。
- `degree`：岗位详情明确的学历要求；缺失则隔离。
- `description` / `requirements`：必须来自岗位详情页正文。
- `apply_url`：官方具体投递页；不得使用搜索结果页或猜出的 ID。

完成数据库更新后导出公网快照：

```powershell
& .\.venv\Scripts\python.exe scripts/export_github_pages.py
git add docs
git commit -m "data: refresh public job snapshot"
git push
```

