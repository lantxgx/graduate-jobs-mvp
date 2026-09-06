# SRC-20260906-fanruan-campus

- company: 帆软
- source_id: `fanruan-campus`
- owner: Codex
- status: integrated / confirmed / reachable
- source URL: https://join.fanruan.com/campus
- official evidence: https://www.fanruan.com/ (the official site links to the Fanruan recruitment portal); the public portal is branded “帆软校园招聘” and separates 校园招聘 from 实习生招聘.
- checked: 2026-09-06

## Evidence and public contract

The official campus list is publicly reachable without login, CAPTCHA, a security challenge, or access-control bypass. The normal page load performs a same-origin `POST` to `/campus` after the initial `GET` establishes a public cookie. The form uses `job_cate[]=5` and `job_cate[]=1`, and returns JSON with `list`, `pageTotal`, `pageSize`, and `dataTotal`.

Each list row has a stable numeric `id`, job title, recruitment mode, job category, locations, duties, requirements, and a public application form URL. The concrete detail URL is `/campus/detail?id=<id>`. Detail pages expose 职位介绍、岗位职责、岗位要求、工作地点 and the official 投递简历 link.

## Collection result

- reported total: 24
- pages traversed: 3 (`pageSize=10`, `pageTotal=3`)
- unique listing IDs: 24
- accepted: 24
- quarantined: 0
- details fetched: 24/24
- created: 18
- updated: 6 (the six rows written during the corrected retry were reconciled idempotently)
- deactivated: 0
- snapshot_complete: true

The source's `校招` mode is mapped to the product's `全职` value because the official portal provides a separate 实习生招聘 channel. Scope-only location labels such as 海外地区、港澳台地区 and country-only labels are removed from city facets; evidenced city entries are preserved. No location is inferred from a code or a description.

## Implementation and verification

Changed:

- `crawler/adapters/fanruan.py`
- `crawler/adapters/__init__.py`
- `crawler/source_registry.py`
- `config/sources.json`
- `tests/test_fanruan_adapter.py`
- `tests/test_adapter_registry.py`

Commands:

```powershell
python -m crawler.source_registry --source-file config/sources.json
python -m crawler.worker --source fanruan-campus
python C:\Users\lantx\.codex\skills\maintain-campus-job-data\scripts\validate_source.py --project-root . --source-id fanruan-campus --min-jobs 3
python -m unittest discover -s tests -v
```

The focused adapter tests and the full suite pass (123 tests). Source validation passes all gates, including official confirmation, public reachability, integration, active-job contract, and latest crawl success.

Next action: include the generated public snapshot in the next export and publish batch; do not retry this source before its normal 12-hour schedule unless the public contract materially changes.
