# SRC-20260908-public-probe-sinopec

- State: blocked
- Company: 中国石化
- Official URL: `https://job.sinopec.com/`
- Ownership evidence: official page title is `中国石化招聘网站`; the public application contains a campus recruitment route.
- Probe: one bounded public request to the campus position endpoint discovered from the official page bundle on 2026-09-08.
- Evidence: `POST https://job.sinopec.com/api/upgrade/homepage/selectPositionList` with the public page-shaped payload `{page:1,limit:20,keyword:""}`.
- Result: HTTP 200 returned `{"code":"E000001","message":"已过应聘截止时间，无法操作","data":null,"success":false}`; no concrete current position list or detail was available.
- Decision: skip for this pass. Do not publish an empty source or retry the expired recruitment batch.
