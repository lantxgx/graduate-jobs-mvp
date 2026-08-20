"""Create conservative source entries for roster companies that already have an official URL."""
from __future__ import annotations
import json
from pathlib import Path

ROSTER=Path('data/company-onboarding-roster.json'); SOURCES=Path('config/sources.json')
def main():
    roster=json.loads(ROSTER.read_text(encoding='utf-8')); sources=json.loads(SOURCES.read_text(encoding='utf-8'))
    existing={str(s.get('url','')).rstrip('/') for s in sources}; added=0
    for e in roster['companies']:
        url=e.get('official_url')
        if not url or e.get('status')=='录入成功' or url.rstrip('/') in existing: continue
        sid=f"roster-{int(e['rank']):03d}"
        if any(s.get('id')==sid for s in sources): continue
        sources.append({'id':sid,'company':e['company'],'name':e['company']+'校园招聘（名录执行）','url':url,'mode':'custom_html','adapter':'custom_html','max_jobs':20,'snapshot_complete':False,'campus_only':True,'enabled':True})
        existing.add(url.rstrip('/')); added+=1
    SOURCES.write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8'); print({'added':added,'total_sources':len(sources)})
if __name__=='__main__': main()
