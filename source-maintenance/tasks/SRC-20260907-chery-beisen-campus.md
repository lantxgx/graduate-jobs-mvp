# SRC-20260907-chery-beisen-campus

- company: 奇瑞汽车
- source: `chery-beisen-campus`
- status: integrated
- owner: Codex
- official public source: `https://chery.zhiye.com/campus`
- ATS: Beisen/Zhiye
- scope: campus recruitment

## Public evidence

- The public portal is company-branded and exposes the 校园招聘 category.
- The public listing API returned 2226 campus records with stable IDs and concrete job fields; detail routes are publicly readable.
- No login, CAPTCHA, or access-control bypass is used.

## Collection plan

- Use a bounded public category-filtered run with page size 50 and no artificial delay.
- Keep `snapshot_complete=false` because this integration is still a sampled/operational snapshot for the catalog.

## Collection result

- `jobs_found=2226`, `created=2226`, `updated=0`
- Source validation passed; the public sample remains explicitly incomplete.
