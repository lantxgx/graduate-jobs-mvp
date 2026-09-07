# SRC-20260914-nuro-greenhouse-careers

- company: Nuro
- source_id: `nuro-greenhouse-careers`
- official careers page: `https://www.nuro.ai/careers`
- public board: `https://boards-api.greenhouse.io/v1/boards/nuro/jobs?content=true`
- adapter: existing Greenhouse adapter
- state: candidate; parser repair ready; awaiting normal crawl cooldown

## Evidence

- Nuro's official Careers page is reachable over HTTPS and identifies itself as `Careers | Nuro`.
- The public Greenhouse board returns Nuro postings with concrete official apply URLs.
- The board contains concrete campus-like titles including `Software Engineer, AI Platform - Intern` and `Software Engineer, AI Platform - New Grad`.
- The source is limited to `intern`, `new grad`, or `graduate` titles and remains `snapshot_complete=false`.

## Bounded result

- Worker command: `python -m crawler.worker --source nuro-greenhouse-careers`.
- Result: `crawl_produced_no_qualified_concrete_jobs`.
- The two concrete roles have substantial official descriptions, but no independent requirements/qualifications section that the current quality gate can map without invention.
- Jobs created: 0; existing data unchanged.

## Decision

The reusable Greenhouse parser now recognizes `About You` headings; focused tests pass and offline normalization accepts both Nuro campus-like records. The existing one-hour crawl cooldown is preserved, so the normal worker/scheduler can perform the next bounded run after cooldown without deleting failure evidence or forcing a retry.
