# SRC-20260912-instacart-greenhouse-careers

- company: Instacart
- source_id: `instacart-greenhouse-careers`
- official careers page: `https://www.instacart.careers/`
- public board: `https://boards-api.greenhouse.io/v1/boards/instacart/jobs?content=true`
- adapter: existing Greenhouse adapter
- state: candidate; bounded integration in progress

## Evidence

- The official Instacart careers domain is reachable over HTTPS.
- The public Greenhouse board returns Instacart-branded postings and concrete apply URLs.
- A naive external keyword check found one `intern` substring, but the concrete title is `Director IT, Internal Audit`; it is not an internship or new-grad role. The adapter's word-boundary filter correctly excluded it.

## Bounded result

- Worker command: `python -m crawler.worker --source instacart-greenhouse-careers`.
- Result: `crawl_produced_no_qualified_concrete_jobs` because the public board contains no qualified campus role in the bounded response.
- Jobs created: 0; existing data unchanged.

## Decision

Pause this source as having no qualified campus jobs. Do not retry without new public evidence.
