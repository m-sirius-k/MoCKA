import argparse,csv,hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).parent.parent
INFIELD=ROOT/'data'/'storage'/'infield'/'RAW'
EVENTS=ROOT/'data'/'events.csv'
INFIELD.mkdir(parents=True,exist_ok=True)
UTC=timezone.utc

def mask(t):
    t=re.sub(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}','[EMAIL]',t)
    t=re.sub(r'sk-[A-Za-z0-9]{20,}','[APIKEY]',t)
    t=re.sub(r'(?i)password\s*[:=]\s*\S+','password=[MASKED]',t)
    return t

def get_prev():
    rows=list(csv.reader(open(EVENTS,encoding='utf-8-sig'))) if EVENTS.exists() else []
    return hashlib.sha256(','.join(rows[-1]).encode()).hexdigest()[:16] if rows else 'GENESIS'

def ingest(items,source):
    prev=get_prev()
    ts_f=datetime.now(UTC).strftime('%Y%m%d_%H%M%S')
    new_rows=[]
    for i,item in enumerate(items):
        eid=f'ERAW_{ts_f}_{i:04d}'
        h=hashlib.sha256(f"{eid}{item['ts']}{item['text'][:100]}{prev}".encode()).hexdigest()[:16]
        rec={'event_id':eid,'source':source,'layer':'RAW','title':item['title'],'role':item['role'],'text':item['text'],'timestamp':item['ts'],'hash':h,'prev_hash':prev,'status':'RAW'}
        json.dump(rec,open(INFIELD/f'{ts_f}_{eid}.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
        new_rows.append([eid,item['ts'],source,'raw_ingest','chat_import','chat_raw_ingest.py',item['title'],'cli','internal','in_operation','normal','A','infield/RAW',item['text'][:100],prev,'ingest_complete','RAW','local','chat_pipeline','N/A','N/A',f"hash={h}|source={source}"])
        prev=h
    with open(EVENTS,'a',encoding='utf-8',newline='') as f:
        csv.writer(f).writerows(new_rows)
    print(f'[OK] {len(new_rows)}件 RAW層に投入')

def parse_chatgpt(data):
    items=[]
    for conv in (data if isinstance(data,list) else [data]):
        title=conv.get('title','untitled')
        for node in conv.get('mapping',{}).values():
            msg=node.get('message')
            if not msg: continue
            role=msg.get('author',{}).get('role','unknown')
            parts=msg.get('content',{}).get('parts',[])
            text=' '.join(str(p) for p in parts if isinstance(p,str)).strip()
            if not text: continue
            t=msg.get('create_time')
            ts=datetime.fromtimestamp(t,UTC).strftime('%Y-%m-%dT%H:%M:%S') if t else datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%S')
            items.append({'title':title,'role':role,'text':mask(text),'ts':ts})
    return items

parser=argparse.ArgumentParser()
parser.add_argument('--file',required=True)
parser.add_argument('--source',required=True,choices=['chatgpt','gemini','claude','manual'])
args=parser.parse_args()
fpath=Path(args.file)
if not fpath.exists():
    print(f'[ERR] {fpath}'); exit()
if args.source=='chatgpt':
    items=parse_chatgpt(json.load(open(fpath,encoding='utf-8')))
else:
    items=[{'title':'manual','role':'human','text':mask(open(fpath,encoding='utf-8').read().strip()),'ts':datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%S')}]
ingest(items,args.source)
print(f'[DONE] {args.source} 投入完了')
