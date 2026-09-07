# BATCH-20260907-beisen-skips

本批只对每个新公开入口做了一次单源探测；以下来源没有接入岗位库，后续不重复请求，除非页面或适配器契约发生变化：

| 企业 | 来源 | 结果 |
|---|---|---|
| 传音控股 | `https://transsion.zhiye.com/campus` | 岗位总量超过短探测页数，停止，未写入岗位 |
| 长安汽车 | `https://changan.zhiye.com/campus` | 岗位总量超过短探测页数；已有长安来源，未计为新增 |
| 金发科技 | `https://kingfa.zhiye.com/campus` | 岗位总量超过短探测页数，停止，未写入岗位 |
| 汇顶科技 | `https://goodix.zhiye.com/campus` | 公开岗位请求失败，未写入岗位 |
| 京东方 | `https://boe.zhiye.com/campus` | 详情未形成合格具体岗位，未写入岗位；已有京东方来源 |
| 零跑汽车 | `https://leapmotor.zhiye.com/campus` | 岗位总量超过短探测页数，停止，未写入岗位 |
| 中金公司 | `https://cicc.zhiye.com/campus` | 岗位总量超过短探测页数，停止，未写入岗位 |
| 朗新科技 | `https://longshine.zhiye.com/campus` | 未形成合格具体岗位，停止，未写入岗位 |
| 申能集团 | `https://shenergy.zhiye.com/campus` | 岗位总量超过短探测页数，停止，未写入岗位 |
| 泰格医药 | `https://tigermed.zhiye.com/campus` | 岗位总量超过短探测页数，停止，未写入岗位 |
| 星巴克 | `https://starbucks.zhiye.com/campus` | 详情未形成合格具体岗位，未写入岗位 |
| 万豪 | `https://marriott.zhiye.com/campus` | 岗位总量超过短探测页数，停止，未写入岗位 |
| 科伦药业 | `https://kelun.zhiye.com/campus` | 公开岗位请求失败，未写入岗位 |
| 房多多 | `https://fangdd.zhiye.com/campus` | 公开岗位请求失败，未写入岗位 |
| 旺旺 | `https://wantwant.zhiye.com/campus` | 详情未形成合格具体岗位，未写入岗位 |

所有探测均未使用登录、验证码、代理或访问控制绕过。
