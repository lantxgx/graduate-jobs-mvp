# SRC-20260908-public-probe-oppo-xiaomi

- state: paused
- baseline: 174 companies with active jobs; 7,718 active jobs

## OPPO

- Candidate URL: `https://careers.oppo.com/university/oppo/campus`
- One bounded public request returned HTTP 200, but only an unidentified JavaScript application shell was exposed.
- No existing ATS contract or concrete normalized listing/detail was verified in the fast probe.
- Decision: skip; do not reverse-engineer a custom adapter in this sweep.

## Xiaomi candidate URL

- Candidate URL: `https://xiaomi.jobs.f.mioffice.cn/campus`
- One bounded public request returned HTTP 404.
- Xiaomi already has an integrated source in the catalog; this stale candidate is not a new company.
- Decision: skip and do not retry this URL without a new official entry.
