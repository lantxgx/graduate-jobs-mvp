# SRC-20260909-affirm-greenhouse-careers

- company: Affirm
- source_id: `affirm-greenhouse-careers`
- state: paused
- adapter: existing Greenhouse adapter
- baseline: 177 companies with active jobs; 7,742 active jobs
- official career URL: `https://www.affirm.com/careers`

## Official evidence

- Affirm's official careers page is publicly reachable.
- Public Greenhouse feed: `https://boards-api.greenhouse.io/v1/boards/affirm/jobs?content=true`
- The feed returns 205 concrete jobs with official apply URLs; no login, CAPTCHA, proxy, or access-control bypass used.

## Collection plan

- Run one bounded sample through the existing Greenhouse adapter.
- Keep `snapshot_complete=false`.

## Result

- One bounded worker run returned `crawl_produced_no_qualified_concrete_jobs`.
- No jobs were created or updated; the source was paused with reason `adapter_mismatch`.
- Do not retry without a confirmed Affirm-specific content mapping or new public evidence.
