# SRC-20260908-figma-greenhouse-careers

- company: Figma
- source_id: `figma-greenhouse-careers`
- state: integrated / sampled
- adapter: existing Greenhouse adapter
- snapshot_complete: false

## Official evidence

- Official careers page: `https://www.figma.com/careers/`
- The official page directly exposes Figma job links hosted on `boards.greenhouse.io/figma`.
- Public listing endpoint used by the normal page contract: `https://boards-api.greenhouse.io/v1/boards/figma/jobs?content=true`
- No login, CAPTCHA, proxy, or access-control bypass used.

## Collection result

- Worker command: `python -m crawler.worker --source figma-greenhouse-careers`
- First bounded response: 16 jobs; the Greenhouse payload placed qualifications inside the content body.
- Minimal parser change split recognized official qualification headings from the description.
- Re-run result: 13 qualified jobs updated, 3 missing-requirements observations quarantined.
- Active jobs after cleanup: 13.
- The sample is intentionally bounded; full snapshot is not claimed.

## Validation

- Focused tests: `python -m unittest tests.test_greenhouse_adapter -v` — 5 passed.
- Source validation: `validate_source.py --source-id figma-greenhouse-careers --min-jobs 3` — passed.
- Coverage after integration: `173/300` companies, `7,708` active jobs.

## Changed files

- `config/sources.json`
- `crawler/adapters/greenhouse.py`
- `tests/test_greenhouse_adapter.py`
- generated public snapshot after validation

## Next action

Continue with other official Greenhouse/Lever sources only when the company careers page links the public board; do not treat search-index-only boards as official evidence.
