# SRC-20260906-microsoft-campus

- company: Microsoft
- source_id: source-7c6951f691ebba1f
- official URL: https://jobs.careers.microsoft.com/global/en/search?lc=China&lc=Hong+Kong+SAR&lc=Taiwan&exp=Students+and+graduates&et=Graduate
- checked_at: 2026-09-06
- state: skipped_high_difficulty

## Bounded probe

- One public GET returned HTTP 200 and the Microsoft Careers shell.
- The page is an Eightfold dynamic application, not a concrete server-rendered job list.
- It includes reCAPTCHA and dynamic/cross-domain scripts; no stable public listing/detail contract was identified in the bounded probe.

## Decision

Do not guess private endpoints, bypass reCAPTCHA, or keep probing. No jobs were written. Do not retry unless a stable public API or a new official page contract is provided.
