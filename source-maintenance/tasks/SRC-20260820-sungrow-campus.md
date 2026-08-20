# SRC-20260820-sungrow-campus

- 企业：阳光电源
- 官方归属证据：https://jobs.sungrowpower.com（官网招聘平台，明确区分校园招聘）
- 官方校招入口：https://app.mokahr.com/campus-recruitment/sungrow/94416
- ATS：Moka 公共校园门户，使用渲染后的岗位卡片和详情。
- 采集结果：20 条具体校园岗位写入 SQLite，crawl run 209；`snapshot_complete=false`，按 bounded 采集策略保留后续刷新。
- 适配器：复用 `crawler/adapters/moka.py`，配置 `sungrow-moka-campus`。
