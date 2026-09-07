# SRC-20260912-apple-public-probe

## Apple

- official source: `https://jobs.apple.com/zh-cn/search?location=china-mainland`
- public endpoint observed: `https://jobs.apple.com/api/v1/search`
- result: `campus_scope_and_china_filter_not_verified`

The official public search endpoint responded successfully. The China-location filter returned zero records; an unfiltered request returned India retail positions, not China campus jobs. The response did not establish a stable China campus listing/detail contract, so no job was written.

No private endpoint, CAPTCHA, login, or filter bypass was used.

## Decision

Skip Apple for this sweep. Do not retry unless the official site exposes a verified China campus filter with concrete details.
