# SRC-20260907-smartx-moka-campus

- company: SmartX
- source: `smartx-moka-campus`
- status: blocked
- owner: Codex
- checked_at: 2026-09-07

## Public-source evidence

- Official campus portal: `https://app.mokahr.com/campus_apply/smartx/4183`
- ATS: Moka, using the existing Moka adapter configuration.

## Probe result

- One bounded single-source worker run did not return a job list within the allowed time and produced no accepted jobs.
- A previous run recorded `public_job_list_missing`; no concrete job detail was verified in this batch.
- No jobs were written and no existing jobs were deactivated.

## Stop decision

The public list contract is not reliable enough for fast onboarding. The source has been disabled in `config/sources.json`; do not retry unless the portal behavior or adapter evidence changes.
