# 岗位标准记录 v1

所有企业适配器先输出 `job-record.schema.json` 规定的标准记录，再进入数据库。网页只读取数据库中的 accepted 记录，不直接读取企业网页。

字段原则：

- `source_job_id`、`apply_url`、`evidence.detail_url` 必须来自官方页面，不能根据标题猜测。
- `work_locations` 统一为城市数组；`job_nature` 只允许“全职/实习”。
- `location_hierarchy` 按国家/地区、省份、城市存储；省份未在官网出现时保持空字符串。
- `job_function` 是岗位职能；`major_requirements` 是学生专业要求，两者不能混用。
- `responsibilities`、`qualifications` 必须保留官方原文拆分结果；缺失时记录进入 `quarantined`，不伪造。
- `major_requirements` 可以为空数组，表示官方未明确专业限制；这与“未注明学历”一样要保留事实状态。
- `raw` 保留原始抓取结果，便于审计和重新解析。

推荐流水线：`官方列表/详情 -> 企业适配器 -> 标准 JSON -> 字段校验/隔离 -> SQLite jobs -> API -> 网页`。
