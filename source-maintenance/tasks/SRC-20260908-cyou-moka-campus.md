# SRC-20260908-cyou-moka-campus

- State: paused
- Company: 搜狐畅游
- Source ID: `cyou-moka-campus`
- Official URL: `https://app.mokahr.com/campus-recruitment/cyou-inc/42233`
- Evidence: public page title is `搜狐畅游 - 校园招聘`; the page is a public Moka campus portal with no login or CAPTCHA observed.
- Adapter: reuse existing `moka` adapter.
- Scope: bounded sample up to 20 jobs; `snapshot_complete=false` until full traversal is proven.

## Result

- Worker completed without access-control errors but returned `crawl_produced_no_qualified_concrete_jobs`.
- Jobs created: 0; existing data unchanged.
- Source disabled with `do_not_retry_without_new_evidence`.
