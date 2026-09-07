# SRC-20260910-microsoft-public-probe

## Microsoft

- official career site: `https://jobs.careers.microsoft.com/global/en/search`
- public API observed: `https://apply.careers.microsoft.com/api/pcsx/search`
- result: `access_throttled_and_detail_contract_missing`

The official public career page exposed a public search response for China positions. The bounded response contained listing IDs, titles, and locations, but did not include concrete descriptions, requirements, or apply URLs. A subsequent normal public request returned HTTP 429, so probing stopped immediately.

No login, CAPTCHA solving, private endpoint guessing, proxy, or rate-limit bypass was used. The source was not added to the campus catalog because campus scope and complete detail fields were not proven.

## Decision

Skip Microsoft for this sweep. Do not retry unless a stable public campus-filtered listing/detail contract becomes available.
