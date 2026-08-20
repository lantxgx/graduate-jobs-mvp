# SRC-20260820-luxshare-campus

- 企业：立讯精密
- 官方归属证据：https://www.luxshare-ict.com/careers.html（官网加入我们页明确链接校园招聘）
- 官方校招入口：https://wecruit.hotjob.cn/SU601778b25d83dc072073230a/pb/school.html
- ATS/公开接口：大易 Hotjob；使用公开 `listPosition` 和 `listPositionDetail` 接口。
- 采集结果：1 条具体岗位“2027届校园大使”写入 SQLite，crawl run 成功；详情含毕业届次、职责、要求和官方投递链接。
- 适配器：复用 `crawler/adapters/hotjob.py`，配置 `luxshare-hotjob-campus`。
- 下一步：低频刷新，保留“校园大使”与普通岗位的范围区分。
