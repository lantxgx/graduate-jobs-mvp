# SRC-20260908-public-probe-csg

- State: blocked
- Company: 中国南方电网
- Official URL: `https://zhaopin.csg.cn/`
- Ownership evidence: official recruitment homepage is reachable and its public bundle exposes a campus recruitment page.
- Probe: one bounded inspection of the official page bundle and one public campus-list request on 2026-09-08.
- Evidence: the official bundle exposes `POST /recruitment-dmz/service/webPost/queryPopularPosition` with a page-shaped payload; the request returned `401` with `您的登录状态已失效，请重新登录！`.
- Result: public listing access requires a guest/session token not available from the bounded public page request; no concrete list/detail was obtained without attempting authentication or bypassing access control.
- Decision: skip for this pass. Do not create credentials, bypass access control, or retry without a changed public access contract.
