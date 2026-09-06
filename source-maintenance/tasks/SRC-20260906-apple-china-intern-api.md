# SRC-20260906-apple-china-intern-api

- Company: Apple
- Source ID: `apple-china-intern-api`
- State: implementing
- Scope: China jobs whose official title explicitly identifies an internship

## Official evidence

- Official recruitment entry: https://jobs.apple.com/zh-cn/search?location=china-mainland
- Public search contract: `POST https://jobs.apple.com/api/v1/search`
- Public detail contract: `GET https://jobs.apple.com/api/v1/jobDetails/{id}`
- Concrete detail verified: https://jobs.apple.com/zh-cn/details/114438030
- The official title is `CN-Specialist: Seasonal, Full-Time or Part-Time or Intern`.
- The detail response exposes duties, minimum qualifications, preferred qualifications, China location, and the official detail URL.
- No login, CAPTCHA, proxy, or access-control bypass was used.

## Bounded collection contract

- Query: `China intern`, first public result page only
- Accepted only when the official title contains `intern` or `实习`
- Maximum accepted sample: 3
- `snapshot_complete=false`; the API total is not treated as a complete campus snapshot.
- The bounded sample is expected to contain one qualifying China internship record; ordinary Apple social roles are excluded.

## Implementation

- Adapter: `crawler/adapters/apple.py`
- Registry/config: `crawler/adapters/__init__.py`, `crawler/source_registry.py`, `config/sources.json`
- The adapter preserves the official source ID and detail URL, and requires both duties and qualifications.

## Result

Pending single-source worker and validation. Do not promote or export until the worker result and field gate are recorded here.
