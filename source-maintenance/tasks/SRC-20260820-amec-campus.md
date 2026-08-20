# SRC-20260820-amec-campus

- 企业：中微公司
- 官方归属证据：https://www.amec-inc.com/index.php/index/Lists/index/catid/100.html（官网“招贤纳士”页）
- 官方校招入口：https://app.mokahr.com/campus_apply/amec/4362
- ATS/公开接口：官网明确链接的 Moka 公共校园门户；使用渲染后的公开岗位卡片和详情。
- 核验结果：公开岗位列表和详情可访问，未绕过登录、验证码或安全验证。
- 采集结果：20 条校招岗位写入 SQLite，crawl run 201；另有官方实习入口 `https://app.mokahr.com/campus-recruitment/amec/146254`，crawl run 203 写入 5 条，合计 25 条。
- 适配器：复用 `crawler/adapters/moka.py`，配置 `amec-moka-campus` 和 `amec-moka-internship`。
- 下一步：按调度器低频刷新两个官方 Moka 来源，并保留校招/实习来源区分。
