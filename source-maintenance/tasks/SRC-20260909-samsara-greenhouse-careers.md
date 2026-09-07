# SRC-20260909-samsara-greenhouse-careers

- company: Samsara
- source_id: `samsara-greenhouse-careers`
- state: integrated / sampled
- adapter: existing Greenhouse adapter
- baseline: 177 companies with active jobs; 7,742 active jobs
- official career URL: `https://www.samsara.com/company/careers`

## Official evidence

- Samsara's official careers page is publicly reachable.
- Public Greenhouse feed: `https://boards-api.greenhouse.io/v1/boards/samsara/jobs?content=true`
- The feed returns 256 concrete jobs and includes internship roles with official apply URLs; no login, CAPTCHA, proxy, or access-control bypass used.

## Collection plan

- Use the explicit title keywords to select internship/new-grad roles in a bounded sample.
- Keep `snapshot_complete=false`.

## Result

- One bounded worker run accepted 7 internship jobs; 7 created, 0 updated.
- The sample passed the active-job contract; `snapshot_complete=false` remains.
