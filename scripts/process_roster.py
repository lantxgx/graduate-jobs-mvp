"""Process the company roster sequentially and persist status after every source."""
from __future__ import annotations
import argparse, asyncio, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from crawler.runner import load_sources, crawl_source
from app.db import connect, init_db

ROSTER = Path("data/company-onboarding-roster.json")

def key(value: str) -> str:
    return str(value or "").replace("集团", "").replace("有限公司", "").replace("股份", "").lower()

async def main(limit: int, retry_failed: bool = False, include_disabled: bool = False):
    init_db(); roster=json.loads(ROSTER.read_text(encoding="utf-8")); sources=load_sources()
    by_company={key(s.get("company")): s for s in sources}
    processed=0
    for entry in roster["companies"]:
        if entry.get("status")=="录入成功" or (entry.get("status")=="失败" and not retry_failed): continue
        source=by_company.get(key(entry["company"]))
        if not source or (not source.get("enabled", True) and not include_disabled): continue
        entry["status"]="录入中"; ROSTER.write_text(json.dumps(roster,ensure_ascii=False,indent=2),encoding="utf-8")
        result=await crawl_source(source); error=result.get("error")
        with connect() as conn:
            count=conn.execute("select count(*) from jobs where source_id=? and status='active'",(source["id"],)).fetchone()[0]
        entry["success_jobs"]=count
        if not error and count: entry["status"]="录入成功"; entry["failed_reason"]=None
        elif count: entry["status"]="部分失败"; entry["failed_reason"]=error or "部分岗位未通过质量门禁"
        else: entry["status"]="失败"; entry["failed_reason"]=error or "没有合格岗位"
        if entry["status"] in {"失败", "部分失败"}:
            entry["method"]="手动"
        ROSTER.write_text(json.dumps(roster,ensure_ascii=False,indent=2),encoding="utf-8")
        print(entry["company"], entry["status"], count, entry["failed_reason"])
        processed+=1
        if processed>=limit: break
    print({"processed":processed,"success":sum(e.get("status")=="录入成功" for e in roster["companies"])})

if __name__ == "__main__":
    parser=argparse.ArgumentParser(); parser.add_argument("--limit",type=int,default=5); parser.add_argument("--retry-failed",action="store_true"); parser.add_argument("--include-disabled",action="store_true"); args=parser.parse_args(); asyncio.run(main(args.limit,args.retry_failed,args.include_disabled))
