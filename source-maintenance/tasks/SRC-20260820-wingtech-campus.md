# SRC-20260820-wingtech-campus

- 企业：闻泰科技
- 官方归属证据：http://www.wingtech.com/cn（官网导航明确链接校园招聘）
- 官方校招入口：http://jobs.wingtech.com/campus
- ATS/公开接口：北森公开接口 `/api/Jobad/GetJobAdPageList`，校园/实习分类按页面配置采集。
- 采集结果：1 条具体实习岗位写入 SQLite，crawl run 成功；包含标题、地点、学历、职责、要求和官方详情链接。
- 适配器：复用 `crawler/adapters/beisen.py`，配置 `wingtech-beisen-campus`。
- 下一步：低频刷新，等待更多明确应届/校园岗位发布。
