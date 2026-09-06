# SRC-20260907-xcmg-moka-campus

- company: 徐工集团
- source: `xcmg-moka-campus`
- status: integrated
- checked_at: 2026-09-07

## Official public evidence

- Official ownership page: `https://www.xcmg.com/aboutus/job_center.htm`
- The official page links directly to `https://app.mokahr.com/campus-recruitment/xcmg/148091?locale=zh-CN` as “校园招聘”.
- The public Moka page exposed concrete job detail routes without login, CAPTCHA, or access-control bypass.

## Collection result

- Bounded live probe returned 5 concrete campus jobs; the first two detail pages normalized successfully.
- `snapshot_complete=false`: this is a bounded sample, not a claim that all Moka pages were exhausted.
