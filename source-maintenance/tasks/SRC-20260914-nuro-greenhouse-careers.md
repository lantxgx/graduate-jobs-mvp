# SRC-20260914-nuro-greenhouse-careers

- company: Nuro
- source_id: `nuro-greenhouse-careers`
- official careers page: `https://www.nuro.ai/careers`
- public board: `https://boards-api.greenhouse.io/v1/boards/nuro/jobs?content=true`
- adapter: existing Greenhouse adapter
- state: candidate; bounded integration in progress

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

Pause because the source needs a source-specific parser/quality decision. Do not retry under the fast-pass rule.
