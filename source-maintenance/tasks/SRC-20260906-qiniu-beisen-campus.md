# SRC-20260906-qiniu-beisen-campus

- company: 七牛云
- source_id: qiniu-beisen-campus
- official listing URL: https://campus.qiniu.com/campus/jobs
- ownership evidence: https://www.qiniu.com/ (the listing is on the company-controlled `campus.qiniu.com` domain)
- ATS: 北森
- checked_at: 2026-09-06T17:00:00+08:00
- task state: integrated (bounded/incomplete snapshot)

## Initial public probe

- The official page returned HTTP 200 and exposed the public Beisen endpoint `/api/Jobad/GetJobAdPageList`.
- The endpoint reported 4 records with concrete titles, locations, duties, and requirements.
- No login, CAPTCHA, 403, 429, proxy, or private endpoint was used.
- The configured category scope is campus recruitment (`Category=["2","3"]`); completeness remains false until the worker reconciles the source count and detail gates.

## Worker result

- run status: success
- jobs found: 3
- jobs created: 3
- jobs updated: 0
- jobs deactivated: 0
- active jobs after run: 3
- quarantined observations: 0 recorded for this run
- source validation: passed with `--min-jobs 3`
- `snapshot_complete`: false; this bounded source remains protected from deactivation.

## Next action

Keep this source on low-frequency refresh and do not treat this bounded sample as complete coverage.
