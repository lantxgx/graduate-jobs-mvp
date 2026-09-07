# SRC-20260908-stripe-greenhouse-careers

- company: Stripe
- source_id: `stripe-greenhouse-careers`
- state: paused
- adapter: existing Greenhouse adapter
- baseline: 174 companies with active jobs; 7,718 active jobs
- official career URL: `https://stripe.com/jobs`

## Official evidence

- Stripe's official jobs page is publicly reachable.
- The official public Greenhouse feed `https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true` returns concrete Stripe roles with Stripe-owned apply URLs.
- The feed includes current `New Grad` and `Intern` roles; no login, CAPTCHA, proxy, or access-control bypass used.

## Collection plan

- Run one bounded sample through the existing Greenhouse adapter.
- Keep `snapshot_complete=false`; do not treat the 619-row public board as fully traversed by the bounded run.

## Result

- One bounded worker run returned `crawl_produced_no_qualified_concrete_jobs`.
- No jobs were created or updated; the source was paused with reason `adapter_mismatch`.
- Do not retry without a confirmed Stripe-specific content mapping or new evidence.
