# SRC-20260820-alibaba-campus

- company: 阿里巴巴
- source_id: alibaba-campus
- source_url: https://campus-talent.alibaba.com/campus/index
- official_evidence_url: https://campus-talent.alibaba.com/campus/position?batchId=100000760001
- owner: Codex
- state: integrated

## Evidence

The public Alibaba campus portal exposes a 2027 graduate project and a concrete
position list. The list page reports 486 positions across 49 pages; each sampled
card links to a concrete `/campus/position/<id>` detail page. Detail pages expose
title, work locations, category, graduate project, description, requirements and
an official apply route without login or CAPTCHA.

## Implementation

- Added the reusable `alibaba` adapter using the normal public listing/detail XHR
  traffic observed while loading the portal.
- Initial bounded probe collected 10 detail records sequentially.
- All 10 records passed the active-job quality gate and were inserted into SQLite.
- `snapshot_complete` remains false because the first run is intentionally capped;
  the visible pagination is 49 pages and must be traversed in a later full refresh.

## Verification

```text
python -m crawler.worker --source alibaba-campus
jobs_found=10, created=10, updated=0
```

Next action: extend the adapter's bounded pagination to exhaust all 49 public
pages, then rerun the completeness reconciliation before marking the snapshot
complete.
