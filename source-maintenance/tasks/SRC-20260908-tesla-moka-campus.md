# SRC-20260908-tesla-moka-campus

- State: integrated
- Company: 特斯拉中国
- Source ID: `tesla-moka-campus`
- Official URL: `https://app.mokahr.com/campus-recruitment/tesla/41460`
- Evidence: public page title is `特斯拉中国-校园招聘`; the public Moka portal loaded without login or CAPTCHA.
- Adapter: reuse existing `moka` adapter.
- Scope: bounded sample up to 20 jobs; `snapshot_complete=false` until full traversal is proven.

## Result

- Worker found 16 concrete jobs and created 16 active jobs.
- Eight rows lacked an explicit requirements field and were quarantined with their raw evidence; 8 qualified jobs remain active.
- No existing jobs outside this new source were updated or deactivated.
- Source passed the active-job contract using the existing `moka` adapter.
- `snapshot_complete=false`: this is a bounded sample, not a complete traversal proof.
