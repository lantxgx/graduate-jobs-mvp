# SRC-20260820-huya-campus

- company: 虎牙
- official_url: https://hr.huya.com/campusRecruit/index
- evidence_url: https://api.mokahr.com/v1/jobs/huya?mode=campus&limit=20&offset=0&commitment=1
- state: integrated
- adapter: huya

虎牙官方招聘站公开加载校园招聘页面。页面脚本使用公开 Moka API，接口在正常页面来源与浏览器请求头下返回 2026 届春季校招岗位，`total=3`，本轮 offset=0 一次取得 3 条具体岗位，均含标题、职责/要求、学历、地点和稳定岗位 ID。未访问社会招聘模式，也未绕过登录、验证码或访问控制。

运行命令：

```powershell
& .\\.venv\\Scripts\\python.exe -m crawler.worker --source huya-campus-api
```

结果：accepted=true，jobs_found=3，created=3。`snapshot_complete=false`，后续刷新仍需按公开接口重新核验 total 和岗位变化。
