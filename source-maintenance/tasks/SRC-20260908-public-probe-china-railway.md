# SRC-20260908-public-probe-china-railway

- State: blocked
- Company: 中国铁路
- Official URL: `https://rczp.china-railway.com.cn/`
- Ownership evidence: the official homepage describes itself as the only official recruitment platform of China State Railway Group and a unified platform for recruiting university graduates.
- Probe: one bounded inspection of the official homepage and its publicly loaded JavaScript/API contract on 2026-09-08.
- Evidence: the page exposes `/job/chnldocinfo/mainList`, `/job/chnldocinfo/maindynamic`, and `/job/jmetadwyl/pagedwyl`; the normal page payload is AES-encrypted by the public client script.
- Result: two normal public-contract requests to `mainList` (JSON and browser-form serialization variants) both returned HTTP 200 with application status `500` and message `出现问题！！！`; no concrete job listing/detail was obtained.
- Decision: skip for this pass. Do not add a source or adapter, do not guess a private contract, and do not retry without new official evidence that the endpoint is functioning.
