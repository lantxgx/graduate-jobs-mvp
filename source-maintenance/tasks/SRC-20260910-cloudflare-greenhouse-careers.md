# SRC-20260910-cloudflare-greenhouse-careers

- company: Cloudflare
- source_id: `cloudflare-greenhouse-careers`
- official careers page: `https://www.cloudflare.com/careers/jobs/`
- public board: `https://boards-api.greenhouse.io/v1/boards/cloudflare/jobs?content=true`
- adapter: existing Greenhouse adapter
- state: candidate; bounded integration in progress

## Evidence

- The official Cloudflare Careers page is publicly reachable without login or CAPTCHA.
- The public Greenhouse board returns Cloudflare-branded postings and concrete official Greenhouse apply URLs.
- The bounded board response contains campus-like roles including Software Engineer Intern and EIAM Business Enablement & Operations Intern.
- The source is limited to titles containing `intern`, `new grad`, or `graduate`; `snapshot_complete=false`.

## Bounded result

- Worker command: `python -m crawler.worker --source cloudflare-greenhouse-careers`.
- Result: `crawl_produced_no_qualified_concrete_jobs`.
- Jobs created: 0; existing data unchanged.

## Decision

Pause this source as an adapter mismatch and do not retry without new parser evidence.
