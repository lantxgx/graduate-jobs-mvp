# SRC-20260820-yitu-campus

- 企业：依图科技
- 官方归属证据：https://www.yitutech.com/cn/join-us
- 官方校招入口：https://www.yitutech.com/cn/career?mode=campus
- ATS/公开接口：依图页面脚本公开调用 `https://api.mokahr.com/v1/jobs/yitu-inc?mode=campus`。
- 核验结果：正常公开页面和接口均可访问；返回 5 个开放校招岗位，均有标题、上海地点、职责/任职要求和 Moka 官方申请链接。
- 采集结果：5 条写入 SQLite；初次采集为 bounded snapshot，`snapshot_complete=false`，后续按刷新任务复核。
- 适配器：`crawler/adapters/yitu.py`，仅使用普通公开 GET 响应，不绕过登录、验证码或安全验证。
- 下一步：继续核验第 287 家云从科技。
