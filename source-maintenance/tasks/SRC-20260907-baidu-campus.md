# SRC-20260907-baidu-campus

- company: 百度
- source: `baidu-campus`
- status: blocked
- owner: Codex
- checked_at: 2026-09-07

## Public-source evidence

- Public campus entry: `https://talent.baidu.com/jobs/list`
- The source uses the existing browser JSON discovery path.

## Probe result

- A bounded probe did not return a stable public job list in the allowed short window and was stopped.
- The orphaned run record was repaired to `failed/bounded_probe_timeout`; no jobs were written and no existing jobs were deactivated.

## Stop decision

The source is disabled for this batch. Do not retry unless the public page or adapter contract changes.
