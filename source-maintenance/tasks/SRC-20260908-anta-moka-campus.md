# SRC-20260908-anta-moka-campus

- company: 安踏集团
- source_id: `anta-moka-campus`
- state: paused
- adapter: existing Moka adapter
- baseline: 174 companies with active jobs; 7,718 active jobs
- source URL: `https://campus.anta.com/`

## Scope

Perform one bounded public probe only. Stop on access control, verification, timeout, adapter mismatch, or incomplete job detail; do not repeat without new evidence.

## Official evidence

- Official recruitment URL: `https://campus.anta.com/`
- The public page identifies 安踏体育用品集团有限公司 and exposes the campus recruitment entry.
- The page loads Moka recruitment assets; the existing browser-driven Moka adapter was used.
- Access was public; no login, CAPTCHA, proxy, or access-control bypass was used.

## Collection plan

- Use the existing `moka` adapter only, with a bounded sample and `snapshot_complete=false`.
- Stop on missing public jobs, timeout, incomplete details, or access controls.

## Result

- One worker attempt exceeded the acceptable Moka page wait without returning a bounded listing result.
- No jobs were created or updated; the source was paused with reason `timeout_in_moka_page_collection`.
- This source will not be retried unless new evidence or an adapter change appears.
