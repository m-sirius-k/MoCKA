# -*- coding: utf-8 -*-
"""
MoCKA Heinrich Engine v2
events.dbをハインリッヒ3層に分類し実測比率を算出
v2: Layer2/3分類精度向上 + 未分類ゼロ化
"""
import json, sqlite3, sys, datetime
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

BASE    = Path(r'C:\Users\sirok\MoCKA')
DB_PATH = BASE / 'data' / 'mocka_events.db'
OUT     = BASE / 'data' / 'heinrich_report.json'

LAYER1_TYPES = {
    'MATAKA','CLAIM','INTEGRITY_VIOLATION','CRITICAL',
    'INSTRUCTION_IGNORE','DEPENDENCY_BREAK','FAST_WRONG'
}
LAYER1_KEYWORDS = [
    'fabricat','unauthorized','overwrite','violation',
    'INTEGRITY','capture','捏造','無断','上書き'
]

LAYER2_TYPES = {
    'DANGER','ERROR','INCIDENT','recurrence',
    'SLOW_DRIFT','FORMAT_COLLAPSE','CLAIM',
    'DEPENDENCY_BREAK','FAST_WRONG'
}
LAYER2_KEYWORDS = [
    'error','exception','fail','timeout','エラー',
    '失敗','また','問題','誤って','バグ','bug','broken',
    'できない','動かない','止まった','違う','ちがう',
    'おかしい','変だ','再発','recur','repeat',
    'warning','drift','collapse','invalid','不正',
    'なぜ','どうして','意味がわからん','わからない'
]

LAYER3_TYPES = {
    'WARNING','success_hint','save','collect',
    'collaboration','share','record','broadcast',
    'process','storage','essence_update','claude_mcp'
}
LAYER3_KEYWORDS = [
    'warning','気づき','hint','check',
    'なぜ','確認','verify','ん？','ちょっと',
    '一応','試して','かも','少し','あれ','念のため'
]

def match_keywords(row, keywords):
    text = ' '.join([
        str(row['what_type'] or ''),
        str(row['title'] or ''),
        str(row['why_purpose'] or ''),
        str(row['how_trigger'] or ''),
        str(row['free_note'] or '')
    ]).lower()
    return any(kw.lower() in text for kw in keywords)

def run():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT event_id,what_type,title,why_purpose,how_trigger,free_note,when_ts FROM events")
    rows = cur.fetchall()
    con.close()

    layer1,layer2,layer3 = [],[],[]

    for row in rows:
        wt = str(row['what_type'] or '').upper()
        entry = {
            'event_id': row['event_id'],
            'what_type': row['what_type'],
            'title': (row['title'] or '')[:60],
            'when': row['when_ts']
        }
        if wt in {t.upper() for t in LAYER1_TYPES} or match_keywords(row, LAYER1_KEYWORDS):
            layer1.append(entry)
        elif wt in {t.upper() for t in LAYER2_TYPES} or match_keywords(row, LAYER2_KEYWORDS):
            layer2.append(entry)
        else:
            # 未分類は全てLayer3として捕捉（ヒヤリハット）
            layer3.append(entry)

    L1,L2,L3 = len(layer1),len(layer2),len(layer3)
    total = L1+L2+L3

    ratio_l2 = round(L2/L1,1) if L1>0 else 0
    ratio_l3 = round(L3/L1,1) if L1>0 else 0
    ratio_str = f'1:{ratio_l2}:{ratio_l3}'

    gap_l2 = round((ratio_l2/29)*100,1) if L1>0 else 0
    gap_l3 = round((ratio_l3/300)*100,1) if L1>0 else 0

    report = {
        'generated_at': datetime.datetime.now().isoformat(),
        'total_events': total,
        'heinrich': {
            'layer1_critical':  {'count':L1,'theory':1,  'label':'Critical'},
            'layer2_minor':     {'count':L2,'theory':29, 'label':'Minor'},
            'layer3_near_miss': {'count':L3,'theory':300,'label':'Near-miss'},
            'actual_ratio':  ratio_str,
            'theory_ratio':  '1:29:300',
            'capture_rate': {
                'layer2': f'{gap_l2}%',
                'layer3': f'{gap_l3}%',
            }
        },
        'layer1_samples': layer1[:10],
        'layer2_samples': layer2[:10],
        'layer3_samples': layer3[:10],
    }

    json.dump(report, open(OUT,'w',encoding='utf-8'), ensure_ascii=False, indent=2)

    print(f'Layer1(重大):  {L1}件')
    print(f'Layer2(軽微):  {L2}件')
    print(f'Layer3(ヒヤリ):{L3}件')
    print(f'実測比率: {ratio_str}')
    print(f'Layer2捕捉率: {gap_l2}% / Layer3捕捉率: {gap_l3}%')
    print(f'未捕捉推定: {max(0,int(L1*300-L3))}件')
    return report

if __name__ == '__main__':
    run()
