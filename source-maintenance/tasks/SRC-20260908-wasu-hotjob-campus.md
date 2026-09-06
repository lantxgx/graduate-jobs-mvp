# SRC-20260908-wasu-hotjob-campus

- company: 华数传媒
- source: `wasu-hotjob-campus`
- status: blocked
- owner: Codex
- checked_at: 2026-09-08

## Public-source evidence

- Recruitment portal: `https://wecruit.hotjob.cn/SU62d26fa80dcad42fc9958ed9/pb/index.html#/`
- ATS evidence: public Hotjob endpoint `wecruit/positionInfo/listPosition/SU62d26fa80dc42fc9958ed9` and its public detail endpoint.
- The endpoint returned concrete 2027 campus positions without login, CAPTCHA, or access-control bypass.

## Probe result

- A direct bounded probe once returned 3 positions and complete details, but the formal single-source worker immediately received an empty list from the same public endpoint.
- No jobs were written and no existing jobs were deactivated.
- The source is disabled and excluded from the integrated allowlist; it is not counted toward company coverage.

## Notes

- The roster previously marked the browser shell as unsuccessful. The endpoint is not stable enough for this run, so do not retry it in this batch.
