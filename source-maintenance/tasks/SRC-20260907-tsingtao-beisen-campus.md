# SRC-20260907-tsingtao-beisen-campus

- company: 青岛啤酒
- source: `tsingtao-beisen-campus`
- status: integrated
- owner: Codex
- official public source: `https://tsingtao.zhiye.com/campus`
- ATS: Beisen/Zhiye
- scope: campus recruitment

## Public evidence

- The portal title identifies 青岛啤酒招聘门户.
- The public page exposes a 校园招聘 section and public job listing API.
- A bounded listing probe returned 40 job rows and concrete campus job data without login or CAPTCHA.

## Probe

The source is configured for a two-page sample with campus category filtering and public detail routes. It remains `snapshot_complete=false` until the source is fully traversed.

## Collection result

- `jobs_found=17`, `created=17`, `updated=0`
- Source validation passed; active sample remains intentionally incomplete.
