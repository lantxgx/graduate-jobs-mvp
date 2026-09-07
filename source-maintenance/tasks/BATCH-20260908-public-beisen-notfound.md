# BATCH-20260908-public-beisen-notfound

- State: paused
- Scope: bounded one-request checks of guessed public Beisen tenant URLs.
- Decision: do not register or retry these URLs because each returned HTTP 200 with the generic `Not Found` page and no concrete job list.

| Company | URL | Result |
|---|---|---|
| 海尔 | `https://haier.zhiye.com/campus` | `Not Found` |
| 美的 | `https://midea.zhiye.com/campus` | `Not Found` |
| 紫光 | `https://ziguang.zhiye.com/campus` | `Not Found` |
| 展锐 | `https://unisoc.zhiye.com/campus` | `Not Found` |
| 紫金 | `https://zijin.zhiye.com/campus` | `Not Found` |

No jobs were written and no existing data was changed.
