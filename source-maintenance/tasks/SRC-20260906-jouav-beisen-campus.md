# SRC-20260906-jouav-beisen-campus

- company: 纵横股份（成都纵横自动化技术股份有限公司）
- source_id: jouav-beisen-campus
- state: validating
- official_url: https://www.jouav.com/zh/career
- campus_url: https://jouav.zhiye.com/campus/jobs
- ats: Beisen / zhiye.com

## Evidence

- The official JOUAV career page is reachable over HTTPS and is titled “招贤纳士 - 纵横股份”.
- The public Beisen portal identifies the tenant as “纵横股份”, alias “成都纵横自动化技术股份有限公司”, and exposes separate campus and internship navigation/pages.
- The public campus list is reachable without login or CAPTCHA and exposes a concrete job-list contract.

## Bounded collection

- Initial probe: 20-listing cap, sequential page requests, campus and campus-system internship categories.
- `snapshot_complete=false` for the first integration; this is a bounded sample, not a full-coverage claim.
- Next: run the single-source worker, inspect accepted/quarantined counts, then validate and export only if gates pass.
