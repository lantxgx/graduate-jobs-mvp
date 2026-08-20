# SRC-20260820-shengqu-moka-campus

- company: 盛趣游戏
- owner: Codex
- state: integrated_sampled
- official_url: https://app.mokahr.com/campus-recruitment/shengqu/96336
- adapter: moka
- scope: 校园招聘

## Official evidence

盛趣游戏官网 `https://www.shengqugames.com/` 的招聘链接指向该 Moka 门户。门户标题为“盛趣游戏 - 校园招聘”，公开页面显示 2027 届秋招岗位，页面初始化数据报告 13 个公开岗位，城市/校招分类和具体详情均可访问，无需登录。

## Collection

- command: `python -m crawler.worker --source shengqu-moka-campus`
- run_id: 156
- result: success
- jobs_found: 13
- jobs_created: 13
- jobs_updated: 0
- snapshot_complete: false
- completeness: 已采集公开首轮 13 条，仍保留非完整快照标记

## Validation

13 条岗位已写入 SQLite，均通过岗位质量门禁并具有官方详情/投递链接。后续刷新继续使用同一 Moka 配置，不删除旧岗位。
