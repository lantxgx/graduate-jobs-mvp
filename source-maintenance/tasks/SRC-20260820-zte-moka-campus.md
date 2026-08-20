# SRC-20260820-zte-moka-campus

- company: 中兴通讯
- state: integrated_sampled
- official_url: https://job.zte.com.cn/content/zte-job/cn/campus-recruitment/Recruitment_positions/freshstudent.html
- adapter: moka

## Evidence

中兴通讯官网招聘页明确指向应届生招聘页面，页面公开链接到官方 Moka 校招门户 `https://app.mokahr.com/campus-recruitment/zte/46903`，可见具体岗位和投递入口。

## Collection

- command: `python -m crawler.worker --source zte-moka-campus`
- run_id: 159
- result: success
- jobs_found: 5
- jobs_created: 5
- jobs_updated: 0
- snapshot_complete: false

5 条岗位已通过标准化质量门禁写入 SQLite；首次接入保留非完整快照标记。
