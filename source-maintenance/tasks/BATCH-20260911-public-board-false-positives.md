# BATCH-20260911-public-board-false-positives

本批仅核验公开 Greenhouse 板和官方 Careers 页面，不写入岗位库。

| Candidate | Result | Decision |
|---|---|---|
| Elastic | Public board returned 367 jobs, but the five keyword hits were `internals`/`Internal` phrases in senior or operations titles, not campus jobs | skip |
| Okta | Public board returned one keyword hit tied to an internal-audit title, not a campus role | skip |
| GitLab | Keyword hits were internal-events/internal-audit roles, not internships or new-grad roles | skip |
| HashiCorp | No usable public Greenhouse board response | skip |
| Wiz | No usable public Greenhouse board response | skip |

No source configuration or job data was changed. Do not repeat these probes without new evidence.
