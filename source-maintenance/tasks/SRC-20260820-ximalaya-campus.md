# SRC-20260820-ximalaya-campus

- company: 喜马拉雅
- official_url: http://jobs.ximalaya.com/campus
- evidence_url: http://jobs.ximalaya.com/api/Jobad/GetJobAdPageList
- state: partial_failure
- adapter: beisen

官方入口可公开访问，页面明确区分“校园招聘”和“实习生招聘”，确认属于喜马拉雅招聘门户（Beisen/Zhiye）。公开接口 `POST /api/Jobad/GetJobAdPageList` 返回 `Count=4`，其中 2 条为社会招聘（`CategoryId=1`），校园招聘分类（`CategoryId=2`）当前为 0 条，实习生招聘分类（`CategoryId=3`）为 2 条。

本轮未将社会招聘岗位写入校园岗位库；2 条实习岗位均具备具体标题、上海市地点、职责、要求和官方来源，可作为合格观察记录，但低于首次接入要求的 3 条样本门槛，因此未注册为可运行 source，名录标记为“部分失败”并转人工复核队列。后续官网出现至少 3 条校招/实习岗位后再按 Beisen 适配器重试。

探测命令：

```powershell
$body=@{PageIndex=0;PageSize=20;KeyWords='';SpecialType=0;PortalId='';DisplayFields=@('Category','Kind','LocId','ClassificationOne','WorkWeChatQrCode');Category=@('3')} | ConvertTo-Json -Depth 5
Invoke-WebRequest -Uri 'http://jobs.ximalaya.com/api/Jobad/GetJobAdPageList' -Method Post -Body $body -ContentType 'application/json'
```
