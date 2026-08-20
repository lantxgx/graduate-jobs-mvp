# SRC-20260820-lovol-campus

- company: 潍柴雷沃
- official source: https://lovol.zhiye.com/lw705xzlist
- source type: official company link to Beisen/Zhiye public campus portal
- adapter: `lovol`
- status: integrated

## Evidence and result

潍柴雷沃官网 `https://www.lovol.com` 的校园人才招聘入口链接到 `lovol.zhiye.com`。公开岗位页直接呈现具体岗位标题、岗位类别、工作地点、发布时间、工作职责、任职资格以及官方投递链接。

首轮 bounded collection:

- visible jobs parsed: 10
- accepted and written: 10
- created: 10
- rejected: 0
- snapshot_complete: false（未证明分页穷尽）
- worker: `python -m crawler.worker --source lovol-beisen-campus`

岗位统一经过共享标准化器，未猜测学历、专业或城市；投递链接使用页面中公开的官方 `Portal/Resume/ResumeItem` 链接。

## Next action

后续刷新时检查分页/筛选条件变化，必要时将岗位列表扩展为完整快照。
