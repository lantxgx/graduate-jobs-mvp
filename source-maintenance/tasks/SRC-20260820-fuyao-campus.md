# SRC-20260820-fuyao-campus

- company: 福耀玻璃
- source: https://job.fuyaogroup.com/fuyao/position/index?recruitmentType=CAMPUSRECRUITMENT
- adapter: `fuyao`
- status: integrated
- scope: campus recruitment; public listing and detail pages

## Evidence

The official recruitment domain `job.fuyaogroup.com` serves a campus listing with concrete `.position-item` records and public detail pages at `/fuyao/position/detail`. No login, CAPTCHA, or access-control bypass was used.

## Collection

- bounded first sample: 3 jobs
- accepted: 3
- rejected: 0
- snapshot_complete: false (the source is not proven exhaustive beyond the visible page)
- worker: `python -m crawler.worker --source fuyao-campus`
- result: created 3, updated 0, deactivated 0

The detail pages expose title, city, responsibilities, education, and major requirements. Apply URLs are the official detail URLs. Data was normalized through the shared job normalizer and written to SQLite.

## Next action

Refresh this source on the normal schedule and re-check the campus listing pagination/count before marking it complete.
