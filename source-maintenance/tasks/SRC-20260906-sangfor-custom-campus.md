# SRC-20260906-sangfor-custom-campus

- company: 深信服
- source_id: sangfor-custom-campus
- official listing URL: https://hr.sangfor.com/campucompon/schoolRecruitment
- ownership evidence: https://hr.sangfor.com/ (the portal is on the company's official HR domain and carries the company copyright)
- ATS: company public API behind the normal public page
- checked_at: 2026-09-06T17:30:00+08:00
- task state: blocked (do not retry)

## Public verification

- Normal browser loading returned HTTP 200 and rendered 27 open campus positions.
- The page itself acquired the public token and called `/api/api/Jobs`; a direct unauthenticated request was not reused or bypassed.
- The returned rows contain stable `positionId`, title, duties, requirements, recruitment type, education, city, and opened time.

## Bounded probe result

- The normal public page returned 27 positions and the first page was readable.
- The adapter's second-page request received an empty/non-JSON response, so the run failed before accepting jobs.
- No jobs were published from this source.
- This source is recorded as failed and must not be requested again unless the public source changes materially.

## Next action

Leave the source unintegrated and preserve the failure evidence; do not retry.
