# BATCH-20260908-public-beisen-tenant-skips

- State: blocked
- Probe date: 2026-09-08
- Rule: one bounded public GET per candidate; no retries after a non-career result.
- Result: the following guessed/common tenant URLs all returned HTTP 200 pages titled `Not Found`, with no job cards or concrete detail URLs:
  - 交通银行 — `https://bankcomm.zhiye.com/campus`
  - 浦发银行 — `https://spdb.zhiye.com/campus`
  - 兴业银行 — `https://cib.zhiye.com/campus`
  - 中信银行 — `https://citicbank.zhiye.com/campus`
  - 邮储银行 — `https://psbc.zhiye.com/campus`
  - 光大银行 — `https://cebbank.zhiye.com/campus`
  - 华夏银行 — `https://hxb.zhiye.com/campus`
  - 招商银行 — `https://cmbchina.zhiye.com/campus`
- Decision: do not add these as sources, do not treat HTTP 200 `Not Found` pages as official job portals, and do not retry without a verified official URL.
