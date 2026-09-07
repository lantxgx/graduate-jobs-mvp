# BATCH-20260908-public-board-skips

- State: blocked / bounded public probe only
- Rule: one bounded public probe per new candidate; no repeated requests after a stop signal.

| Candidate | Official careers probe | Public board probe | Decision |
|---|---:|---:|---|
| Coinbase | HTTP 403 / verification page | Greenhouse HTTP 200 | skip; official ownership page is blocked |
| Pinterest | HTTP 403 / verification page | Greenhouse HTTP 200 | skip; official ownership page is blocked |
| MongoDB | HTTP 503 | Greenhouse HTTP 200 | skip; official careers page unavailable |
| Chime | HTTP 403 / verification page | Greenhouse HTTP 200 | skip; official ownership page is blocked |
| Rubrik | HTTP 403 / verification page | Greenhouse HTTP 200 | skip; official ownership page is blocked |
| Twilio | HTTP 200 | worker stopped at `verification_page_detected` | paused; do not retry without new evidence |
| Lattice | HTTP 200 | worker produced no qualified concrete jobs | paused; do not retry without new evidence |
| Roku | HTTP 200 | worker produced no qualified concrete jobs | paused; do not retry without new evidence |
| Hightouch | HTTP 200 | worker produced no qualified concrete jobs | paused; do not retry without new evidence |

These candidates remain unintegrated and no placeholder jobs were created for them.
