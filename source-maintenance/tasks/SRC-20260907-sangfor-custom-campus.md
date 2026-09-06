# SRC-20260907-sangfor-custom-campus

- company: 深信服
- source: `sangfor-custom-campus`
- status: blocked
- owner: Codex
- checked_at: 2026-09-07

## Public-source evidence

- Public campus entry: `https://hr.sangfor.com/campucompon/schoolRecruitment`
- A company-specific public API adapter was available.

## Probe result

- The public request returned an empty/non-JSON response; the adapter failed with `Unexpected end of JSON input`.
- No concrete job was accepted and no existing jobs were deactivated.

## Stop decision

The endpoint is not stable enough for this batch. The source is disabled and will not be retried without new API evidence.
