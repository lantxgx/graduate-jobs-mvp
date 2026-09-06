# SRC-20260907-iflytek-campus-roster

- company: 科大讯飞
- source: `iflytek-campus-roster`
- status: blocked
- owner: Codex
- checked_at: 2026-09-07

## Public-source evidence

- Official recruitment portal: `https://campus.iflytek.com/official-pc/jobList`
- The page identifies the company as 科大讯飞 and publicly exposes a 2027 campus-recruitment project.
- The portal uses the Beisen/iTalent public portal structure and exposes a campus list page and campus detail-page configuration without login or CAPTCHA.

## Probe result

- The existing custom HTML probe did not capture concrete job cards.
- A bounded retry using the reusable Beisen adapter failed at the public job-page request stage with `public_job_page_request_failed`.
- No concrete job detail was accepted; no jobs were written and no existing jobs were deactivated.

## Stop decision

The page has visible recruitment metadata but the current public request contract is not stable enough for fast onboarding. The source is disabled and will not be retried without new API evidence or a targeted adapter repair.
