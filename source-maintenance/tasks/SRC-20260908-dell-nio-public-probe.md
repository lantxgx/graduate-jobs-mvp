# SRC-20260908-dell-nio-public-probe

## 戴尔

- candidate: `https://jobs.dell.com/search-jobs/China`
- result: `public_listing_contract_not_obtained_in_fast_probe`
- The page returned a small client shell without a directly readable campus job list or concrete detail payload in the bounded public check. No private API was guessed and no job was written.

## 蔚来

- candidate: `https://nio.jobs.feishu.cn/campus/position`
- result: `stale_public_url`
- The public entry returned HTTP 404. No login wall or private endpoint was bypassed.

## Decision

Skip both sources for this sweep and do not retry unless a stable official public campus listing/detail contract appears.
