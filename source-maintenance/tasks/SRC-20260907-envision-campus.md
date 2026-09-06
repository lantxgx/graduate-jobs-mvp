# SRC-20260907-envision-campus

- company: 远景科技集团（Envision）
- source_id: envision-campus
- official source: https://envision-career.com/campus-recruitment/envisiongroup/43123/#/jobs
- state: blocked — public portal is reachable, but the bounded detail sample is incomplete
- evidence: the public page is titled 远景校园招聘 and exposes concrete 2027 campus jobs in the rendered public payload
- scope: use the existing Moka adapter with a 10-job bounded sample; keep snapshot_complete=false
- stop rule: stop immediately if detail pages require login/CAPTCHA, lack concrete requirements, or fail the active-job contract
- result: 7 rows were observed; 5 lacked explicit requirements and the source failed the active-job contract. No source promotion.
- cleanup: the 7 probe rows were marked inactive with a quality issue; no jobs were deleted. Existing quarantine evidence was preserved.
- next action: do not retry in this sweep unless the official detail pages expose complete requirements
