# SRC-20260908-hypergryph-moka-campus

- State: integrated
- Company: 鹰角网络
- Source ID: `hypergryph-moka-campus`
- Target scope: campus full-time and internship positions

## Official evidence

- Official recruitment URL: `https://campus.hypergryph.com/campus_apply/hypergryph/26326`
- Page title: `鹰角网络校园招聘`
- Ownership evidence: the page identifies 鹰角网络 and exposes a campus recruitment position-list module.
- ATS evidence: public page loads Moka recruitment assets and exposes Moka initialization data.
- Access: HTTP 200; no login, CAPTCHA, 403, 429, or security verification observed during bounded inspection.
- Adapter plan: reuse existing browser-driven `moka` adapter; no private API reverse engineering.

## Collection plan

- Bounded sample: up to 10 jobs and 10 details.
- `snapshot_complete=false` until full pagination/detail coverage is proven.
- Stop on missing concrete details or access controls.

## Result

- Collected 9 concrete jobs; created 9 active jobs and updated 0.
- All accepted rows include a concrete official apply URL and passed the active-job contract.
- Registry integration uses the existing `moka` adapter; no new adapter code was required.
- Source remains `snapshot_complete=false` because this was a bounded sample rather than a proven full traversal.
- Validation passed with `--min-jobs 3` after registry promotion.
