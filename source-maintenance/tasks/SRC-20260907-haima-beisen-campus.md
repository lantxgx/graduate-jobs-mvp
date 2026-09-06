# SRC-20260907-haima-beisen-campus

- company: 海马物业（海马）
- source_url: https://haima.zhiye.com/campus
- checked_at: 2026-09-07
- state: skipped_low_volume
- adapter: beisen

## Evidence

- The public campus page was reachable without login, CAPTCHA, or access-control bypass.
- The normal public Beisen listing endpoint `https://haima.zhiye.com/api/Jobad/GetJobAdPageList` responded with HTTP 200 for `Category=[2]`.
- The response exposed one concrete campus job, `管培生`, with duties, requirements, employment type, location, and a stable public job ID.

## Decision

- The public campus list contained only 1 concrete job in this bounded probe.
- Per the current fast-sweep rule, sources with fewer than 3 usable jobs are not integrated in this batch.
- Do not retry this source unless new public evidence shows additional campus jobs; no configuration or database changes were made.

## Reproduction

```powershell
$body = @{ PageIndex=0; PageSize=20; KeyWords=''; SpecialType=0; PortalId=''; DisplayFields=@('Category','Kind','LocId','ClassificationOne','WorkWeChatQrCode'); Category=@(2) } | ConvertTo-Json -Depth 4
Invoke-WebRequest -Method Post -Uri 'https://haima.zhiye.com/api/Jobad/GetJobAdPageList' -ContentType 'application/json' -Body $body
```
