# SRC-20260908-hjsd-moka-campus

- State: integrated
- Company: 欢聚集团
- Source ID: `hjsd-moka-campus`
- Official URL: `https://app.mokahr.com/apply/hjsd/48`
- Evidence: public page title is `欢聚集团招聘官网`; public Moka portal loaded without login or CAPTCHA.
- Adapter: reuse existing `moka` adapter.
- Scope: bounded sample up to 20 jobs; `snapshot_complete=false` until full traversal is proven.

## Result

- Worker found 20 concrete jobs and created 20 active jobs.
- No existing jobs were updated or deactivated.
- Source passed the active-job contract using the existing `moka` adapter.
- `snapshot_complete=false`: this is a bounded sample, not a complete traversal proof.
