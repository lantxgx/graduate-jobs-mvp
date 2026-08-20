# SRC-20260820-zulong-moka-campus

- company: 祖龙娱乐
- owner: Codex
- state: integrated_sampled
- official_url: https://campus.zulong.com/
- final_url: https://campus.zulong.com/
- adapter: moka
- scope: 校园招聘/实习公开岗位

## Evidence

公开页面标题为“祖龙娱乐-校园招聘”，无需登录即可访问岗位分类和具体岗位详情；详情链接使用 `https://campus.zulong.com/#/job/<uuid>`。页面可见多个岗位分类及实习岗位入口，符合校园招聘范围。

## Collection

- command: `python -m crawler.worker --source zulong-moka-campus`
- run_id: 154
- result: success
- jobs_found: 3
- jobs_created: 3
- jobs_updated: 0
- snapshot_complete: false
- completeness: 首次受控样本，未声称完整覆盖

## Notes

已通过 Moka 通用适配器获取 3 条具体岗位并写入 SQLite。由于本次为受控首批采集，页面剩余分类/岗位未在本任务中全部遍历；后续刷新需继续分页/分类核验后再考虑完整快照。

## Validation

- 3 条岗位均有稳定 source_job_id、具体标题、城市、学历、职责/要求和官方 apply_url。
- source registry 已同步，前端快照将在批次导出后更新。
