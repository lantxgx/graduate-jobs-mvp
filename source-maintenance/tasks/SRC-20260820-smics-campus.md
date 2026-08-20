# SRC-20260820-smics-campus

- 企业：中芯国际
- 官方归属证据：https://www.smics.com/
- 官方校招入口：https://smics.zhiye.com/campus
- ATS/公开入口：官网导航明确链接到上述北森入口；普通公开访问得到过期/404页面，岗位接口请求失败。
- 核验结果：官方归属成立，但当前公开入口没有可核验的逐岗列表和详情；未绕过访问控制，也未猜测岗位。
- 采集结果：0 条写入 SQLite；crawl run 202 成功记录失败原因 `public_job_page_request_failed`。
- 适配器：复用 `crawler/adapters/beisen.py` 做一次受控验证，未将不完整响应写入岗位库。
- 下一步：保留为手动补录候选，后续仅在官方入口恢复具体岗位时重试。
