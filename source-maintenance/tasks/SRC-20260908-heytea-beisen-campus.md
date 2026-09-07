# SRC-20260908-heytea-beisen-campus

- company: 喜茶
- source_id: `heytea-beisen-campus`
- source_url: `https://heytea.zhiye.com/campus`
- adapter: existing Beisen adapter
- state: paused after bounded completeness stop; not integrated

## Bounded attempt

- One sequential worker attempt was run: `python -m crawler.worker --source heytea-beisen-campus`.
- The public Beisen source stopped at `beisen_page_limit_before_source_count` before a source total could be established.
- No jobs were accepted or published.

## Decision

Skip this source under the fast-pass rule. Do not retry without a parser/completeness change or new public evidence.
