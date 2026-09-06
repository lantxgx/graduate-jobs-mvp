# BATCH-20260907-new-official-sweep

## Scope

Bounded read-only probe of three companies not represented by an active job source. Public company pages were used to verify ownership; no login, CAPTCHA solving, private API guessing, or access-control bypass was attempted.

## Skipped without integration

- 银河通用机器人（Galbot）：official site `https://www.galbot.com/` links to `https://app.mokahr.com/social-recruitment/yinhetongyong/165929#/`. The reachable portal is explicitly social recruitment, not a campus/graduate source. No campus-system job list was observed.
- 奥比中光（Orbbec）：official site `https://www.orbbec.com/` links to `https://www.orbbec.com/careers/`. The page is a general careers page for R&D/business/administrative roles and did not expose a concrete public campus list/detail contract in this bounded probe.
- 影石创新（Insta360）：the official recruitment page `https://www.insta360.com/cn/jobs` explicitly identifies campus/internship recruitment and links the public Feishu portal `https://arashivision.jobs.feishu.cn/campus`. A bounded run stopped at the first detail because it failed the required field quality gate; see `SRC-20260907-insta360-feishu-campus.md`.

## Result

No jobs were accepted from this sweep. Insta360 is retained only as documented blocked evidence and must not be retried in the next sweep.
