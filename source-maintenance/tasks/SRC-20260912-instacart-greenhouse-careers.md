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
- The bounded board response contains one internship-like title; the source is limited to `intern`, `new grad`, or `graduate` titles and remains `snapshot_complete=false`.

## Bounded result

- Worker command: `python -m crawler.worker --source instacart-greenhouse-careers`.
- Result: `crawl_produced_no_qualified_concrete_jobs`.
- Jobs created: 0; existing data unchanged.

## Decision

Pause this source as an adapter mismatch. Do not retry without new parser evidence.
