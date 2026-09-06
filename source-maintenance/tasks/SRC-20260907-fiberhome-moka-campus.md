# SRC-20260907-fiberhome-moka-campus

- company: 烽火通信
- source: `fiberhome-moka-campus`
- status: blocked
- owner: Codex
- checked_at: 2026-09-07

## Public-source evidence

- Public Moka portal: `https://app.mokahr.com/campus-recruitment/whfhtx/73922`

## Probe result

- A bounded worker probe did not return a public job list in the short allowed window and was stopped before another request.
- The orphaned run was marked failed with `bounded_probe_timeout`; no jobs were written and no existing jobs were deactivated.

## Stop decision

The portal is too slow or unstable for this batch. It is disabled and will not be retried without changed evidence.
