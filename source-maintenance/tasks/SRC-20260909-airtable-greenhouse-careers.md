# SRC-20260909-airtable-greenhouse-careers

- company: Airtable
- source_id: `airtable-greenhouse-careers`
- state: integrated / sampled
- adapter: existing Greenhouse adapter
- baseline: 176 companies with active jobs; 7,736 active jobs
- official career URL: `https://www.airtable.com/careers`

## Official evidence

- Airtable's official careers page is publicly reachable.
- Public Greenhouse feed: `https://boards-api.greenhouse.io/v1/boards/airtable/jobs?content=true`
- The feed returns 16 concrete Airtable jobs with official apply URLs; no login, CAPTCHA, proxy, or access-control bypass used.

## Collection plan

- Run one bounded sample through the existing Greenhouse adapter.
- Keep `snapshot_complete=false`.

## Result

- One bounded worker run accepted 6 jobs; 6 created, 0 updated.
- The sample passed the active-job contract; `snapshot_complete=false` remains because the board was not fully traversed.
