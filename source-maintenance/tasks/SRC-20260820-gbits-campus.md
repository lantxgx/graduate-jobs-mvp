# SRC-20260820-gbits-campus

- company: 吉比特
- official_url: https://hr.g-bits.com/
- evidence_url: https://joinserver.g-bits.com:8666/humanResource/recruitmentExtranet/ExtrannetCampusPost/queryRecuitPost
- state: partial_failure
- adapter: public_json_probe

吉比特官方校招页公开调用 `POST /humanResource/recruitmentExtranet/ExtrannetCampusPost/queryRecuitPost`。正常页面请求体为 `currentPage=1,pageSize=20,recruitsType=CAMPUS_RECRUITING`，本轮返回 `count=1`，仅有“VIP客服（韩语）”一条校招正式岗位，包含职责、要求、深圳地点和稳定岗位 ID。由于低于首批自动接入 3 条岗位门槛，未写入岗位库，名录标记部分失败并转人工复核。
