"""Discover and directly verify official career URLs for the next roster entries.

Search results are only candidates; a URL is written back only after a direct
HTTP fetch succeeds and the page contains the company name or recruitment text.
"""
from __future__ import annotations
import base64,json,re,sys
from pathlib import Path
from urllib.parse import quote,urlparse,parse_qs
from urllib.request import Request,urlopen
from bs4 import BeautifulSoup
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

def search(company):
    html=urlopen(Request('https://www.bing.com/search?q='+quote(company+' 校园招聘 官网'),headers={'User-Agent':'Mozilla/5.0'}),timeout=20).read()
    out=[]
    for a in BeautifulSoup(html,'html.parser').select('li.b_algo h2 a'):
        href=a.get('href',''); q=parse_qs(urlparse(href).query); encoded=(q.get('u') or [''])[0]
        if encoded.startswith('a1'):
            try: href=base64.b64decode(encoded[2:]+'===').decode('utf-8')
            except Exception: pass
        if href.startswith(('http://','https://')): out.append(href)
    return out
def verify(company,url):
    try:
        r=urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=15); text=r.read(500000).decode('utf-8','ignore').lower()
        return r.status==200 and (company.lower() in text or any(k in text for k in ('校园招聘','校招','campus','careers','招聘','职位'))) and len(text)>200
    except Exception: return False
def main(limit=20):
    p=Path('data/company-onboarding-roster.json'); d=json.loads(p.read_text(encoding='utf-8')); n=0
    for e in d['companies']:
        if n>=limit: break
        if e.get('official_url') or e.get('status')!='待录入': continue
        for u in search(e['company']):
            host=urlparse(u).netloc.lower()
            if any(x in host for x in ('bing.com','baidu.com','zhihu.com','zhipin.com','liepin.com')): continue
            if verify(e['company'],u):
                e['official_url']=u; e['url_status']='已验证'; e['method']='自动优先'; n+=1; print(e['company'],u); break
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8'); print({'verified':n})
if __name__=='__main__': main(int(sys.argv[1]) if len(sys.argv)>1 else 20)
