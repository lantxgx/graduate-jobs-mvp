# SRC-20260908-datadog-greenhouse-careers

- company: Datadog
- source_id: `datadog-greenhouse-careers`
- state: integrated / sampled
- adapter: existing Greenhouse adapter
- baseline: 174 companies with active jobs; 7,718 active jobs
- official career URL: `https://careers.datadoghq.com/`

## Official evidence

- Datadog's official careers page is publicly reachable.
- Public Greenhouse feed: `https://boards-api.greenhouse.io/v1/boards/datadog/jobs?content=true`
- The feed returns concrete jobs and includes internship roles; no login, CAPTCHA, proxy, or access-control bypass used.

## Collection plan

- Run one bounded sample through the existing Greenhouse adapter.
- Keep `snapshot_complete=false` unless pagination and detail completeness are proven.

## Result

- After the Greenhouse adapter added title-keyword selection and case-insensitive requirement headings, one bounded worker run accepted 2 internship jobs; 2 created, 0 updated.
- `snapshot_complete=false`; the public board was not claimed complete.
