# SRC-20260820-smartsenstech-campus

- 企业：思特威
- 官方归属证据：https://www.smartsenstech.com/（官网页脚公开链接到校园招聘）
- 官方校招入口：https://campus.smartsenstech.com/
- ATS 入口：https://app.mokahr.com/campus-recruitment/smartsenstech1/56088
- 核验结果：官方校园招聘页公开跳转到 Moka 校招职位页；普通页面加载获得具体岗位卡片及详情。
- 采集结果：20 条岗位通过标准化门禁并写入 SQLite；本次为 bounded 采集，`snapshot_complete=false`。
- 适配器：复用 `crawler/adapters/moka.py`，未绕过登录、验证码或安全验证。
- 下一步：继续第 292 家韦尔股份。
