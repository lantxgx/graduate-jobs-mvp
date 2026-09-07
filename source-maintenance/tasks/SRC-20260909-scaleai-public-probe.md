# SRC-20260909-scaleai-public-probe

- company: Scale AI
- candidate source: `scaleai` Greenhouse board
- official careers page: `https://scale.com/careers`
- public board probe: `https://boards-api.greenhouse.io/v1/boards/scaleai/jobs?content=true`
- state: deferred; not integrated

## Evidence and stop rule

- The official Careers page was reachable over HTTPS and identified itself as Scale AI Careers.
- The public Greenhouse board returned 215 jobs, including three campus-like titles: Software Engineering Intern (Summer 2027), Software Engineer - New Grad, and University Recruiter, Contract.
- In the bounded HTTP check, the official page did not expose a direct Greenhouse/job-detail link. A browser verification attempt did not complete promptly.
- No job was accepted and no source configuration or database row was added.

## Decision

Ownership/detail evidence is insufficient for a fast, auditable integration. Defer this candidate and do not repeat the probe without a new official link or a stable page response.
