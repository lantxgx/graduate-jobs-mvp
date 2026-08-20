# SRC-20260820-czbank-campus

- 企业：浙商银行
- 官方招聘首页：https://zp.czbank.com.cn/zpweb/
- 官方岗位页：https://zp.czbank.com.cn/zpweb/planController/gotoIndex.mvc?pageType=1
- 岗位接口：https://zp.czbank.com.cn/zpweb/planController/getPost.mvc?zpType=1
- 核验结果：官方页面和岗位接口均可公开访问；接口响应 `code=1`，`postTotalPage=0`，`dataList=[]`。
- 采集结果：0 条，不写入岗位库。
- 失败原因：当前官方接口没有具体可申请校招岗位；未绕过登录、验证码或访问控制。
- 后续：按名录继续处理下一家待录入企业；后续刷新仍检查该官方入口。
