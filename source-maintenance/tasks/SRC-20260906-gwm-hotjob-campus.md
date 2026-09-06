# SRC-20260906-gwm-hotjob-campus

- company: 长城汽车
- source_id: `gwm-hotjob-campus`
- owner: Codex
- status: integrated / confirmed / reachable / sampled
- official source evidence: https://zhaopin.gwm.cn/
- final public source: https://zhaopin.gwm.cn/SU692d3058ea11b01b6c54d0ea/pb/index.html
- checked: 2026-09-06

## Evidence and result

The official 长城汽车 recruitment domain redirects to the public Hotjob campus portal. The portal's public list and detail endpoints were accessed without login, CAPTCHA, security verification or bypass. Existing Hotjob parsing was reused.

The bounded first page returned 5 stable post IDs. Four detail records had complete duties and requirements and were accepted. One record had no explicit requirements and was preserved as a quarantined observation by the source-specific completeness gate; it was not published. This is an intentional sample, so `snapshot_complete=false`.

- listed observations: 5
- accepted active jobs: 4
- quarantined: 1 (`missing_requirements`)
- detail requests: 5/5
- deactivated: 0

The source is not treated as complete and must not be refreshed before its normal cooldown unless the public contract changes.
