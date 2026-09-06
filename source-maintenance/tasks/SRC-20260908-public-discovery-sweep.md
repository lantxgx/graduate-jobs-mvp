# SRC-20260908-public-discovery-sweep

本轮只做一次公开入口探测；未满足“无需登录即可取得列表和详情”的企业不进入 `config/sources.json`，后续不重复请求。

## 上汽集团：跳过

- 官方人才招聘入口：https://www.saicmotor.com/chinese/rlzy/index.html
- 最终校园入口：https://saic-recruit.saicmotor.com/recruit/pc/#/collegeRecruit
- 页面正常加载公开招聘前端；前端暴露职位接口 `/recruit/api/recruit/position/get/list`。
- 对公开列表接口做一次无登录请求，返回 `401` / `用户未登录`；无公开岗位列表和详情可供入库。
- 结论：`login_wall`，未绕过登录，不配置来源，不再重试，除非出现新的公开接口证据。

## 广汽集团：跳过

- 官方招聘页面：https://www.gac.com.cn/cn/talent#join
- 页面能看到“校园招聘”栏目，但当前公开内容提示历史校园招聘已结束；当前可见的是社会招聘/实习/海外等栏目，未取得可核验的在招校园岗位列表和逐岗详情。
- 结论：`no_current_public_campus_jobs`，不猜测岗位、不配置来源。

## 奇瑞：跳过

- 官方招聘页面：https://www.chery.cn/others/recruit/
- 页面为人才招募宣传/招聘入口页面，本次公开 HTML 未发现可核验的校园岗位列表、逐岗职责和申请详情。
- 结论：`no_concrete_public_campus_jobs`，不配置来源。

