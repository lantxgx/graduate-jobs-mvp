# 标准化岗位样本

`companies-10.json` 是供产品和其他 AI 审阅的第一批标准化样本。含有岗位的企业来自当前数据库的 accepted 岗位；没有公开可入库岗位的企业只保留公司壳记录并标记为 `blocked`，不虚构岗位。

重新导出：

```powershell
& .\.venv\Scripts\python.exe scripts/export_standard_jobs.py --limit 10
```
