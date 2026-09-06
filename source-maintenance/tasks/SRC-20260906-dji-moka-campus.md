# SRC-20260906-dji-moka-campus

- company: DJI 大疆
- source_id: `dji-moka-campus`
- owner: Codex
- status: integrated / confirmed / reachable / sampled
- official ownership evidence: https://careers.dji.com/zh-CN/campus
- final public source: https://apply.careers.dji.com/campus-recruitment/dji/143359
- checked: 2026-09-06

## Evidence

DJI's official careers campus page links directly to the public Moka campus portal. The portal title identifies “DJI 大疆校园招聘”, exposes the campus job list without login or CAPTCHA, and provides concrete public job detail routes under `#/job/<UUID>`. The portal's initial data reports 139 open campus jobs. The source is a Moka portal and the existing Moka adapter was reused.

## Bounded collection result

- collected: 5 concrete jobs sequentially
- details fetched: 5/5
- created: 5, updated after city-parser correction: 5
- active jobs: 5
- snapshot_complete: false (the portal reports 139 jobs; this onboarding run intentionally samples 5)
- deactivated: 0
- rejected/quarantined: 0

The detail header's location is preferred over a city marker accidentally present in a title such as “（深圳）”. The five accepted records have explicit details, degree evidence, stable UUIDs, official detail/apply URLs, and normalized city values.

## Changed and verified

- `config/sources.json`: added the bounded DJI source.
- `crawler/source_registry.py`: allowlisted the verified Moka source.
- `crawler/adapters/moka.py`: prefer explicit detail-header location over title-like list-card text.
- `tests/test_moka_jobs.py`: regression test for the city mapping.

Commands run:

```powershell
python -m crawler.source_registry --source-file config/sources.json
python -m crawler.worker --source dji-moka-campus
python C:\Users\lantx\.codex\skills\maintain-campus-job-data\scripts\validate_source.py --project-root . --source-id dji-moka-campus --min-jobs 3
```

The source is intentionally not marked complete. A later bounded refresh may collect more jobs only after the normal cooldown; do not treat this sample as the portal's total coverage.
