# BATCH-20260906-easy-source-sweep

## Sweep result

- Baseline after the latest successful source: 84 companies with active jobs, 3265 active jobs.
- The current enabled registry contains 61 sources with no active jobs.
- 32 of those sources already have source-specific failure evidence in `source-maintenance/tasks/`; they are not retried.
- The remaining 29 are historical duplicate registry rows, disabled/legacy discovery rows, or entries without a verified reusable adapter. They are not promoted or crawled merely because a URL exists.
- No new company was counted from duplicate URLs belonging to companies already represented by another active source.
- Microsoft was given one bounded public-page probe; the result was an Eightfold/reCAPTCHA dynamic shell without a stable listing/detail contract, so it was recorded as high difficulty and skipped.

## Skip rule applied

Sources with prior `403`, `404`, timeout, security verification, missing concrete detail fields, adapter mismatch, or no verified public job contract remain documented and skipped. No proxy, login, CAPTCHA bypass, guessed endpoint, or repeated failure request was used in this sweep.

## Current next queue

Continue with a newly verified official public source that has concrete listing/detail evidence and either an existing adapter or a small bounded adapter. Do not re-run the 32 failed sources or count updates to existing companies as new coverage. Push only after ten genuinely new companies have been added.
