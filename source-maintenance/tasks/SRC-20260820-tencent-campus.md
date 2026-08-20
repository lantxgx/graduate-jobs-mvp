# SRC-20260820-tencent-campus

- company: 腾讯
- source_id: roster-002
- source_url: https://join.qq.com/post.html?query=p_1
- official_evidence_url: https://join.qq.com/post_detail.html?postid=1282707398326592512
- state: integrated

腾讯官方校招页公开展示 2027 校园招聘岗位，并通过公开接口返回岗位列表和详情。
详情包含岗位名称、岗位描述、岗位要求、招聘类别、工作城市及官方投递详情页。

本轮使用公开页面的 `searchPosition` 与 `getJobDetailsByPostId` 请求，按顺序采集
10 个具体岗位。10/10 通过岗位质量门禁并写入 SQLite；由于页面显示共有 113 个岗位，
本轮仍是有上限的初始样本，`snapshot_complete` 保持 false。

验证命令：

```text
python -m crawler.worker --source roster-002
jobs_found=10, created=10, updated=0
```
