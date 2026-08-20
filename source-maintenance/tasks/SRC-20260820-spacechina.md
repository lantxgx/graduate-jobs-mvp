# SRC-20260820-spacechina

- company: 中国航天科技
- state: blocked_public_access
- official_url: http://www.spacechina.com/n25/n2014703/n2014708/index.html
- final_url: https://www.spacetalent.com.cn/
- adapter: none (blocked before public listing)

## Evidence

中国航天科技集团官网 `http://www.spacechina.com/n25/index.html` 的“加入我们/人才招聘”入口公开跳转到 `https://www.spacetalent.com.cn/`。目标站点首页在普通 HTTP 请求下返回 BotD 刷新频率/反自动化校验脚本，未提供可直接读取的具体校园岗位列表和详情。

## Collection

- result: blocked_public_access
- jobs_found: 0
- jobs_created: 0
- snapshot_complete: false
- reason: 未绕过 BotD、安全验证或登录限制；保留人工复核队列，未创建来源配置，未删除任何旧数据。

## Next action

如后续站点在不需要绕过安全验证的公开页面提供具体岗位，再按 Moka/自建页面重新核验；否则通过后台手动录入并附官方公告证据。
