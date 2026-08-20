# SRC-20260820-qianxin-campus

- 企业：奇安信
- 官方校招入口：https://campus.qianxin.com/campus/jobSearch?type=shixishen
- 列表接口：https://campus.qianxin.com/Job/Campus/lists?callback=x
- 核验结果：页面与脚本可公开访问，接口响应 `code=200`，但 `data.jobs=[]`；响应仅返回城市、职类和招聘类型筛选项，没有具体岗位卡片或详情链接。
- 采集结果：0 条，不写入岗位库。
- 失败原因：当前公开接口没有具体岗位；不绕过登录、验证码或安全验证。
- 后续：下次刷新仍先检查同一官方接口，出现具体岗位后再实现适配器并做 3–20 条首轮样本。
