# SRC-20260820-douyu-campus

- company: 斗鱼
- official_url: https://zhaopin.douyu.com/intern
- evidence_url: https://zhaopin.douyu.com/zp/japi/portal/position/list
- state: manual
- adapter: public_json_probe

斗鱼官网“加入我们”页面链接至独立官方招聘站 `zhaopin.douyu.com`，页面公开加载职位列表接口。按页面正常请求分别以 `recruitType=1`（校园招聘）和 `recruitType=2`（实习招聘）请求 `POST /zp/japi/portal/position/list`，返回 `code=0` 且 `data.total=0`、`records=[]`。当前没有具体岗位可入库，未写入空数据，名录标记为失败并保留待后续复核。

探测请求体：

```json
{"workPlaces":[],"positionCates":[],"positionName":"","page":1,"pageSize":10,"recruitType":1}
```
