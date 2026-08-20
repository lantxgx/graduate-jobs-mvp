# SRC-20260820-sanqi-campus

- company: 三七互娱
- official_url: https://zhaopin.37.com/index.php?m=Home&c=campus&a=index
- evidence_url: https://zhaopin.37.com/index.php?m=Home&c=campus&a=getIndexPage&key=&post_type=&place_type=&page=1
- state: partial_failure
- adapter: sanqi

三七互娱官方招聘站校园页公开调用 `GET /index.php?m=Home&c=campus&a=getIndexPage`，返回 JSON 岗位列表。首批有界采集最多 10 条，取得 8 条含岗位名称、城市、职责、要求和官方 Moka 投递链接的合格岗位；其余记录缺少可用岗位标识或详情字段，已由质量门禁隔离。来源保持 `snapshot_complete=false`，后续继续按分页/接口结果复核。

运行结果：`sanqi-campus`，`jobs_found=8`，`jobs_created=8`。
