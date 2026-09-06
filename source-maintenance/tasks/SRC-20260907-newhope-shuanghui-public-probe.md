# SRC-20260907-newhope-shuanghui-public-probe

## 新希望

- candidate: `https://newhope.zhiye.com/campus`
- result: `public_job_list_contract_missing`
- The page was reachable, but the standard public Beisen listing endpoint did not return a job payload. No private endpoint was guessed and no job was written.

## 双汇

- candidate: `https://shuanghui.zhiye.com/campus`
- result: `below_minimum_public_sample`
- The public campus filter returned only one concrete job. It is below the project's minimum source sample gate, so the source was not integrated or padded with non-campus rows.

## Decision

Skip both sources for this sweep and do not retry unless the official portal exposes a stable multi-job campus listing contract.
