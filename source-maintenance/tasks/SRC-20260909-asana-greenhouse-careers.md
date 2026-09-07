# SRC-20260909-asana-greenhouse-careers

- company: Asana
- source_id: `asana-greenhouse-careers`
- state: paused
- adapter: existing Greenhouse adapter
- baseline: 176 companies with active jobs; 7,736 active jobs
- official career URL: `https://asana.com/jobs`

## Official evidence

- Asana's official jobs page is publicly reachable.
- Public Greenhouse feed: `https://boards-api.greenhouse.io/v1/boards/asana/jobs?content=true`
- The feed returns concrete Asana jobs with official apply URLs; no login, CAPTCHA, proxy, or access-control bypass used.

## Collection plan

- Run one bounded sample through the existing Greenhouse adapter.
- Keep `snapshot_complete=false`; do not claim full board coverage.

## Result

- One bounded worker run returned `crawl_produced_no_qualified_concrete_jobs`.
- No jobs were created or updated; the source was paused with reason `adapter_mismatch`.
- Do not retry without a confirmed Asana-specific content mapping or new public evidence.
