# SRC-20260820-tbea-campus

- 企业：特变电工
- 官方归属证据：https://www.tbea.com/join.html（页面明确区分校园招聘）
- 官方校招入口：https://wecruit.hotjob.cn/SU612f55eebef57c0616450aa2/pb/school.html
- ATS：大易 Hotjob；使用公开岗位列表和详情接口。
- 采集结果：20 条具体校园岗位写入 SQLite，crawl run 成功；bounded snapshot，后续低频刷新。
- 适配器：复用 `crawler/adapters/hotjob.py`，配置 `tbea-hotjob-campus`。
