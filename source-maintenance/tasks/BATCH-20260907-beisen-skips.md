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
| 佳能中国 | `https://canon.zhiye.com/campus` | 详情未形成合格具体岗位，未写入岗位 |
| 电装集团 | `https://denso.zhiye.com/campus` | 详情未形成合格具体岗位，未写入岗位 |
| 高露洁 | `https://colgate.zhiye.com/campus` | 详情未形成合格具体岗位，未写入岗位 |
| 希尔顿 | `https://hilton.zhiye.com/campus` | 岗位总量超过短探测页数，停止，未写入岗位 |
| 百胜中国 | `https://yumchina.zhiye.com/campus` | 公开岗位请求失败，未写入岗位 |
| 蓝帆医疗 | `https://bluesail.zhiye.com/campus` | 单源运行未形成合格具体岗位，已暂停，未写入岗位 |
| 泰尔茂医疗 | `https://terumo.zhiye.com/campus` | 单源运行未形成合格具体岗位，已暂停，未写入岗位 |
| 泰格医药 | `https://tigermed.zhiye.com/campus` | 岗位总量超过短探测范围，按快速筛选规则暂停，未重复获取 |
| 星巴克（新来源） | `https://starbucks.zhiye.com/campus` | 详情未形成合格具体岗位，已暂停 |
| 万豪 | `https://marriott.zhiye.com/campus` | 岗位总量超过短探测范围，按快速筛选规则暂停 |
| 喜茶、优衣库 | `https://heytea.zhiye.com/campus`、`https://uniqlo.zhiye.com/campus` | 已有冷却状态，说明此前已探测；本轮不重复请求，暂不接入 |
| 科伦药业、房多多 | `https://kelun.zhiye.com/campus`、`https://fangdd.zhiye.com/campus` | 公开岗位请求失败，已暂停 |
| 中国人寿、中国人保、北京银行、联通数科 | 对应 `*.zhiye.com/campus` | 公开接口/详情未形成合格岗位，已暂停 |
| 华安财险、华安基金、中国信达 | 对应 `*.zhiye.com/campus` | 公开接口/详情未形成合格岗位，已暂停 |
| 百度、网易游戏、完美世界 | `roster-003`、`roster-010`、`roster-027` | 公开页面未提供可安全识别的具体岗位卡片，已暂停，不再重复请求 |
| 蚂蚁集团 | `roster-014` | 公开页面未提供可安全识别的具体岗位卡片，已暂停，不再重复请求 |
| vivo、平安银行、虎牙 | `roster-043`、`roster-106`、`roster-024` | 公开页面未提供可安全识别的具体岗位卡片，已暂停，不再重复请求 |
| 中国银行、知乎、莉莉丝 | `roster-122`、`roster-022`、`roster-029` | 公开页面未提供可安全识别的具体岗位卡片，已暂停，不再重复请求 |

所有探测均未使用登录、验证码、代理或访问控制绕过。
