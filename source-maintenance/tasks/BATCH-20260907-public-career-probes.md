# BATCH-20260907-public-career-probes

本批仅做一次公开入口快速筛查；未发现具体校招岗位的来源不进入配置，也不重复请求。

## 跳过来源

### 高通

- Official URL: https://www.qualcomm.cn/company/careers
- Result: HTTP 200，但页面只有招聘介绍、全球招聘入口和账户提示，没有公开具体校园岗位列表或详情链接。
- Decision: `no_concrete_public_job_list`; skip without adapter work.

### IBM

- Candidate URL: https://careers.ibm.com/job/search
- Result: HTTP 404，未获得岗位列表或详情。
- Decision: `http_404`; skip without retry.

### Dell

- Candidate URL: https://jobs.dell.com/search-jobs/China
- Result: HTTP 200 后跳转至 Dell 招聘平台 404 页面。
- Decision: `redirected_404`; skip without retry.

以上来源均未写入 `config/sources.json`，没有产生岗位数据，也没有使用登录、验证码或访问控制绕过。
