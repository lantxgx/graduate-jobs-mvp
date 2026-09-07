# SRC-20260908-webank-moka-campus

- State: blocked
- Company: 微众银行
- Source ID: `webank-moka-campus`
- Target scope: campus full-time and internship positions

## Official evidence

- Official recruitment URL: `https://campus.webank.com/m/campus-recruitment/webankhr/18005`
- Page title: `微众银行 - 校园招聘`
- Ownership evidence: the page identifies 微众银行 and exposes a campus recruitment site with a concrete position-list module.
- ATS evidence: public page loads Moka recruitment assets and exposes Moka initialization data.
- Access: HTTP 200; no login, CAPTCHA, 403, 429, or security verification observed during bounded inspection.
- Adapter plan: reuse existing browser-driven `moka` adapter; no private API reverse engineering.

## Collection plan

- Bounded sample: up to 10 jobs and 10 details.
- `snapshot_complete=false` until full pagination/detail coverage is proven.
- Stop on missing concrete details or access controls.

## Result

- Single-source command: `python -m crawler.worker --source webank-moka-campus`
- Worker result: `public_job_list_missing`; jobs found/created/updated: `0 / 0 / 0`.
- Decision: skip and disable. Do not retry without a changed public list contract or adapter evidence.
