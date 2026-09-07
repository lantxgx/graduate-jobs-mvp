# SRC-20260909-databricks-greenhouse-careers

- company: Databricks
- source_id: `databricks-greenhouse-careers`
- state: paused
- adapter: existing Greenhouse adapter
- baseline: 178 companies with active jobs; 7,749 active jobs
- official career URL: `https://www.databricks.com/company/careers`

## Official evidence

- Databricks' official careers page is publicly reachable.
- Public Greenhouse feed: `https://boards-api.greenhouse.io/v1/boards/databricks/jobs?content=true`
- The feed returns 870 concrete jobs and includes explicit New Grad and Intern roles with official apply URLs; no login, CAPTCHA, proxy, or access-control bypass used.

## Collection plan

- Use explicit title keywords to select only New Grad/Intern roles in a bounded sample.
- Keep `snapshot_complete=false`.

## Result

- One bounded worker run returned `crawl_produced_no_qualified_concrete_jobs`.
- No jobs were created or updated; the source was paused with reason `adapter_mismatch`.
- Do not retry without a confirmed Databricks-specific content mapping or new public evidence.
