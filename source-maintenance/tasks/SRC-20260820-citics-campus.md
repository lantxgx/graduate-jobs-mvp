# 中信证券校园招聘（citics-campus）

- company: 中信证券
- source URL: https://careers.citics.com/campus/headquarters
- official ownership: 中信证券官方招聘域名 `careers.citics.com`
- adapter: `citics`
- state: integrated — 2026-08-20

## Public contract

- listing: `POST https://global-kong.citics.com/api/v1/recruit/getPositionList`
- detail: `POST https://global-kong.citics.com/api/v1/recruit/getPositionInfo`
- required public parameter: `sysNo=CSE001`, `recruitType=08`, `deptype=Headquarter`, `practice=1`

## Result

- bounded listing count: 1
- accepted jobs: 1
- created: 1
- snapshot_complete: false (bounded campus internship sample)
- detail coverage: 1/1
- old active jobs changed: no

岗位列表和详情均来自官网公开请求，已标准化写入 SQLite；未访问登录后投递接口。
