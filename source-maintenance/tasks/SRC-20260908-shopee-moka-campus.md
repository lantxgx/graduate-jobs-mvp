# SRC-20260908-shopee-moka-campus

- State: paused
- Company: Shopee
- Source ID: `shopee-moka-campus`
- Official URL: `https://app.mokahr.com/campus-recruitment/shopee/2962`
- Evidence: public page title is `Shopee 校园招聘`; public Moka portal loaded without login, CAPTCHA, or access-control bypass.
- Adapter: reuse existing `moka` adapter.
- Scope: bounded sample up to 20 jobs; `snapshot_complete=false` until full traversal is proven.

## Result

- Worker completed without access-control errors but returned `crawl_produced_no_qualified_concrete_jobs`.
- Jobs created: 0; existing data unchanged.
- Source disabled with `do_not_retry_without_new_evidence`.
