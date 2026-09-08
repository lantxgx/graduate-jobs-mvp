# BATCH-20260908-greenhouse-followup-skips

- State: blocked / bounded public probe only
- Rule: no retries after a stop signal or empty public contract.

| Candidate | Result | Decision |
|---|---|---|
| Fivetran | worker stopped at `verification_page_detected` | paused; do not retry |
| Cockroach Labs | worker produced no qualified concrete jobs | paused; do not retry |
| Cloudinary | official page reachable, Greenhouse board returned 404 | skip |
| Contentful | official page returned 429 and Greenhouse board had 0 jobs | skip |

No placeholder jobs were created for these candidates.
