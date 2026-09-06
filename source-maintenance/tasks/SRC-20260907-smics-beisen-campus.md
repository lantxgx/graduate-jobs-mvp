# SRC-20260907-smics-beisen-campus

- company: 中芯国际
- source: `smics-beisen-campus`
- status: blocked
- owner: Codex
- checked_at: 2026-09-07

## Public-source evidence

- Public campus entry: `https://smics.zhiye.com/campus`
- ATS identified as Beisen and an existing Beisen adapter was available.

## Probe result

- A bounded single-source run failed at the public job-page request stage with `public_job_page_request_failed`.
- No concrete job detail was accepted and no existing jobs were deactivated.

## Stop decision

The source is not reliable enough for the fast onboarding batch. It has been disabled in `config/sources.json`; do not retry without new page/adapter evidence.
