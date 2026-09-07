# SRC-20260908-anta-moka-campus

- State: blocked
- Company: 安踏集团
- Source ID: `anta-moka-campus`
- Owner/agent: Codex
- Started at: 2026-09-08
- Target scope: campus full-time and campus internship positions

## Official evidence

- Official recruitment URL: `https://campus.anta.com/`
- Page title: `安踏集团校园招聘官网`
- Ownership evidence: the public page's SEO content names `安踏体育用品集团有限公司`; the page exposes campus recruitment navigation and a concrete job-list module.
- ATS evidence: the public page loads Moka recruitment assets and exposes Moka `org_id=antahr` and `site_id=142914` in the page metadata.
- Access: HTTP 200; no login, CAPTCHA, 403, 429, or security verification observed during bounded inspection.
- Public detail contract: rendered links use Moka `#/job/<uuid>` routes; the existing browser-driven Moka adapter can traverse list and detail pages without reverse-engineering encrypted APIs.

## Collection plan

- Use the existing `moka` adapter only.
- Initial bounded sample: up to 20 public jobs and 20 details.
- Keep `snapshot_complete=false` until pagination and detail coverage are proven.
- Stop and record a blocker if the rendered list is empty, details lack concrete duties/requirements, or access becomes restricted.

## Result

- Single-source command: `python -m crawler.worker --source anta-moka-campus`
- Worker result: failed with `crawl_produced_no_qualified_concrete_jobs`; jobs found/created/updated: `0 / 0 / 0`.
- Decision: skip and disable this source. The public page is reachable, but the current bounded Moka collection did not produce a publishable concrete job. Do not retry without new official evidence or an adapter change.
