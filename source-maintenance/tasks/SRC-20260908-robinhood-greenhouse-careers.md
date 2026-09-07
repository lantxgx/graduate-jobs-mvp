# SRC-20260908-robinhood-greenhouse-careers

- company: Robinhood
- source_id: `robinhood-greenhouse-careers`
- state: integrated / sampled
- adapter: existing Greenhouse adapter
- snapshot_complete: false

## Official evidence

- Official careers page: `https://careers.robinhood.com/`
- The public careers listing is backed by Robinhood's Greenhouse board token `robinhood`.
- Public listing endpoint used by the normal page contract: `https://boards-api.greenhouse.io/v1/boards/robinhood/jobs?content=true`
- The listing includes concrete new-graduate roles such as Business Analyst (New Grad); no login, CAPTCHA, proxy, or access-control bypass used.

## Collection result

- Worker command: `python -m crawler.worker --source robinhood-greenhouse-careers`
- First bounded response: 10 qualified jobs; 10 created, 0 updated, 0 deactivated.
- Minimal parser change: accept Greenhouse qualification headings `What you bring` / `What you'll bring` without requiring a trailing colon.
- The sample is intentionally bounded; full snapshot is not claimed.

## Validation

- Focused tests: `python -m unittest tests.test_greenhouse_adapter -v` — 6 passed.
- Source validation: active-job and contract gates passed; registry promotion was then reconciled.

## Changed files

- `config/sources.json`
- `crawler/adapters/greenhouse.py`
- `crawler/source_registry.py`
- `tests/test_greenhouse_adapter.py`
- generated public snapshot after validation

## Next action

Continue with another low-effort official Greenhouse/Lever source. Skip sources requiring verification, login, or custom parser development and record the reason instead.
