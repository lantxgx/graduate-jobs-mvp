# SRC-20260908-webank-moka-campus

- company: 微众银行
- source_id: `webank-moka-campus`
- state: paused
- adapter: existing Moka adapter
- baseline: 174 companies with active jobs; 7,718 active jobs
- source URL: `https://campus.webank.com/m/campus-recruitment/webankhr/18005`

## Official evidence

- The official campus recruitment URL identifies 微众银行 and loads a public Moka recruitment page.
- Access was public; no login, CAPTCHA, proxy, or access-control bypass was used.

## Collection plan

- Use the existing `moka` adapter for one bounded sample only; do not claim complete coverage.
- Stop on missing public jobs, incomplete details, or access controls.

## Result

- One bounded worker attempt returned `public_job_list_missing`.
- No jobs were created or updated; the source was paused with reason `public_job_list_missing; adapter_mismatch`.
- Do not retry without new public-list evidence or a source-specific adapter change.
