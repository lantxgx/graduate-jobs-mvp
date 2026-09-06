# SRC-20260907-shlab-campus

- company: 上海人工智能实验室
- source_id: shlab-campus
- official source: https://www.shlab.org.cn/joinus/campus?mode=campus
- public API: `GET https://www.shlab.org.cn/api/getJobList?mode=campus&limit=7`
- state: integrated — bounded sample accepted; snapshot remains incomplete
- evidence: the official join page labels the section “校园招聘”; public list and detail pages are reachable without login or CAPTCHA
- result: one repaired bounded run accepted 10 concrete internship jobs; two public API pages were traversed, each accepted job has explicit description, requirements, Shanghai location, stable ID, and official detail URL
- completeness: `snapshot_complete=false`; the sample is capped at 10 and is not claimed as full coverage
- next action: keep low-frequency refresh; count one new company toward the next 10-company publication batch
