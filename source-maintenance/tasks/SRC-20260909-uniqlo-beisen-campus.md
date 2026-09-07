# SRC-20260909-uniqlo-beisen-campus

- company: 优衣库
- source_id: `uniqlo-beisen-campus`
- source_url: `https://uniqlo.zhiye.com/campus`
- adapter: existing Beisen adapter
- state: paused after bounded completeness stop; not integrated

## Bounded attempt

- One sequential worker attempt was run: `python -m crawler.worker --source uniqlo-beisen-campus`.
- The public source stopped at `beisen_page_limit_before_source_count` before a source total could be established.
- No jobs were accepted or published.

## Decision

Skip this source under the fast-pass rule. Do not retry without a parser/completeness change or new public evidence.
