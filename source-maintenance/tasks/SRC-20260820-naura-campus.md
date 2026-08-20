# SRC-20260820-naura-campus

- 企业：北方华创
- 官方归属证据：https://www.naura.com/（官网“加入我们-校园招聘”链接到招聘门户）
- 官方校招入口：https://career.naura.com/campus
- ATS/公开接口：北森公开接口 `https://career.naura.com/api/Jobad/GetJobAdPageList`，页面分类 2/3 为校园/实习。
- 核验结果：公开岗位列表和详情可访问，未遇到登录、验证码或安全验证。
- 采集结果：37 条具体校招/实习岗位写入 SQLite，crawl run 200；`snapshot_complete=false`，因为当前配置为受控 bounded run。
- 适配器：复用 `crawler/adapters/beisen.py`，配置 `naura-beisen-campus`。
- 下一步：按调度器低频刷新，后续验证分页总数和岗位过期变化。
