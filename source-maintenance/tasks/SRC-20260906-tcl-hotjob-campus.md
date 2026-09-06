# SRC-20260906-tcl-hotjob-campus

- company: TCL
- source_id: `tcl-hotjob-campus`
- owner: Codex
- status: integrated / confirmed / reachable / sampled
- official ownership evidence: https://campus.tcl.com/
- final public source: https://wecruit.hotjob.cn/SU64893571bef57c16d356b99e/pb/school.html
- checked: 2026-09-06

## Evidence

The TCL campus page is publicly reachable and links its campus recruitment entry to the Hotjob portal. The portal exposes a public JSON listing endpoint and concrete detail endpoint; no login, CAPTCHA, security challenge, or access-control bypass was used. The existing Hotjob adapter was reused.

## Bounded collection result

- collected: 5 concrete jobs sequentially
- details fetched: 5/5
- accepted: 5
- rejected/quarantined: 0
- active jobs: 5
- created: 5
- snapshot_complete: false (this is an intentional 5-job onboarding sample)
- deactivated: 0

The official listing rows supplied stable post IDs, and each detail supplied duties, requirements, location, recruitment type and an official detail/apply route. The source remains sampled because the first run is capped below the portal total.

Next action: do not refresh before the normal source cooldown; later runs may increase the bounded sample after the source policy is explicitly changed.
