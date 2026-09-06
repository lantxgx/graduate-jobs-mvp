# BATCH-20260907-moka-discovery

对搜索发现但尚未进入项目配置的 Moka 入口做了一次公开页面核验。以下页面均 HTTP 200，但页面标题和正文均为“当前网页已关停”，未出现具体岗位列表或详情，因此不纳入来源配置，也不重复请求：

- https://app.mokahr.com/campus-recruitment/chaitin/92701
- https://app.mokahr.com/campus-recruitment/digital-engine/92713
- https://app.mokahr.com/campus-recruitment/klww/67963
- https://app.mokahr.com/campus-recruitment/antahr/102448
- https://app.mokahr.com/campus-recruitment/tesla/55955
- https://app.mokahr.com/campus-recruitment/vanke/41519
- https://app.mokahr.com/campus-recruitment/bostonscientific/102308

Decision: `closed_public_portal`; no jobs written, no login/CAPTCHA/access-control bypass, no retry planned unless an official site later exposes a new active campus URL.
