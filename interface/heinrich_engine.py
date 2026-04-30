# -*- coding: utf-8 -*-
"""MoCKA Heinrich Engine v4 - 実態最適分類版"""
import json, sqlite3, sys, datetime
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

BASE    = Path(r'C:\Users\sirok\MoCKA')
DB_PATH = BASE / 'data' / 'mocka_events.db'
OUT     = BASE / 'data' / 'heinrich_report.json'

# ===== Layer1: 重大事故 =====
# AI違反・制度違反・データ破壊・セキュリティ侵害・MATAKA(またか！)
LAYER1_EXACT = {
    'MATAKA', 'CLAIM',
    'ai_violation', 'governance_degradation',
    'INTEGRITY_VIOLATION', 'CRITICAL',
    'INSTRUCTION_IGNORE', 'DEPENDENCY_BREAK',
    'security', 'FAST_WRONG',
}
LAYER1_KW = [
    'unauthorized', 'violation', 'integrity',
    'fabricat', '捏造', '無断', '上書き', 'overwrite',
    'credential', 'token_exposed', 'leak',
    'GPT無断', 'ai_violation', 'oauth',
]

# ===== Layer2: 軽微な事故 =====
# エラー・失敗・設定ミス・品質問題・再発記録
LAYER2_EXACT = {
    'DANGER', 'ERROR', 'INCIDENT', 'recurrence',
    'SLOW_DRIFT', 'FORMAT_COLLAPSE',
    'config_error', 'environment_error', 'data_quality',
    'MORPHO_DANGER', 'MATAKA_AUTO',
}
LAYER2_KW = [
    'error', 'fail', 'timeout', 'exception', 'broken',
    'エラー', '失敗', 'バグ', 'bug', 'invalid',
    'できない', '動かない', '止まった', '問題',
    'recur', 'また', '再発', 'repeat', '繰り返し',
    'drift', 'collapse', 'degradation', 'wrong',
    'なぜ', 'どうして', 'わからない', '意味がわからん',
    'omit', 'skip', 'miss', '省略', '漏れ',
]
# Layer2でもこれらタイプは除外(日常操作)
LAYER2_EXCLUDE = {
    'essence_update', 'claude_mcp', 'collect', 'save',
    'process', 'broadcast', 'success_hint', 'storage',
    'collaboration', 'share', 'record', 'phl_decision',
    'ingest', 'RAW', 'generation', 'OPERATION',
    'RE_REDUCED', 'playwright_capture', 'response',
    'success_great', 'UPDATED', 'caliber', 'cli',
}

# ===== Layer3: ヒヤリハット =====
# 全ての日常操作・記録・共有・収集・AIとのインタラクション
# → Layer1/Layer2に該当しない全て
LAYER3_EXACT = {
    'essence_update', 'claude_mcp', 'collect', 'save',
    'process', 'broadcast', 'success_hint', 'storage',
    'collaboration', 'share', 'record', 'phl_decision',
    'ingest', 'RAW', 'generation', 'OPERATION',
    'RE_REDUCED', 'playwright_capture', 'response',
    'success_great', 'UPDATED', 'caliber', 'cli',
}

def classify(row):
    wt   = str(row['what_type'] or '').strip()
    titl = str(row['title'] or '').lower()
    why  = str(row['why_purpose'] or '').lower()
    free = str(row['free_note'] or '').lower()
    full = ' '.join([wt.lower(), titl, why, free])

    # Layer1: 厳密判定
    if wt in LAYER1_EXACT:
        return 1
    if any(k.lower() in full for k in LAYER1_KW):
        if wt not in LAYER2_EXCLUDE and wt not in LAYER3_EXACT:
            return 1

    # Layer2: エラー・失敗系（日常操作タイプは除外）
    if wt in LAYER2_EXACT and wt not in LAYER2_EXCLUDE:
        return 2
    if wt not in LAYER3_EXACT and wt not in LAYER2_EXCLUDE:
        if any(k.lower() in full for k in LAYER2_KW):
            return 2

    # Layer3: それ以外全て（日常操作・観測記録）
    return 3

def run():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT event_id,what_type,title,why_purpose,how_trigger,free_note,when_ts FROM events")
    rows = cur.fetchall()
    con.close()

    buckets = {1:[], 2:[], 3:[]}
    type_dist = {}

    for row in rows:
        layer = classify(row)
        wt = str(row['what_type'] or 'unknown')
        type_dist.setdefault(wt, {1:0,2:0,3:0})
        type_dist[wt][layer] += 1
        buckets[layer].append({
            'event_id':  row['event_id'],
            'what_type': row['what_type'],
            'title':     (row['title'] or '')[:60],
            'when':      row['when_ts']
        })

    L1,L2,L3 = len(buckets[1]),len(buckets[2]),len(buckets[3])
    total = L1+L2+L3

    r2 = round(L2/L1,1) if L1>0 else 0
    r3 = round(L3/L1,1) if L1>0 else 0
    g2 = round((r2/29)*100,1)  if L1>0 else 0
    g3 = round((r3/300)*100,1) if L1>0 else 0
    missing = max(0, int(L1*300-L3))

    report = {
        'generated_at': datetime.datetime.now().isoformat(),
        'total_events': total,
        'heinrich': {
            'layer1_critical':  {'count':L1,'theory':1,  'label':'Critical/重大事故'},
            'layer2_minor':     {'count':L2,'theory':29, 'label':'Minor/軽微な事故'},
            'layer3_near_miss': {'count':L3,'theory':300,'label':'Near-miss/ヒヤリハット'},
            'actual_ratio':  f'1:{r2}:{r3}',
            'theory_ratio':  '1:29:300',
            'capture_rate': {
                'layer2': f'{g2}%',
                'layer3': f'{g3}%',
                'interpretation': 'MoCKAが捕捉できている事案の割合'
            },
            'missing_estimate': missing,
            'insight': (
                'Layer2が少ない=軽微事故の記録経路が不足。'
                'またか！ボタンの活用でLayer2を増やすことが制度成熟への最短経路。'
            )
        },
        'layer1_samples': buckets[1][:10],
        'layer2_samples': buckets[2][:10],
        'layer3_samples': buckets[3][:10],
        'type_distribution': {
            k: v for k,v in
            sorted(type_dist.items(), key=lambda x:-(x[1][1]*100+x[1][2]*10+x[1][3]))[:25]
        }
    }

    json.dump(report, open(OUT,'w',encoding='utf-8'), ensure_ascii=False, indent=2)

    print('='*55)
    print('MoCKA Heinrich Engine v4 - 実態最適分類版')
    print('='*55)
    print(f'Layer1 (重大事故):   {L1:5d}件  [{",".join(sorted(LAYER1_EXACT)[:4])}...]')
    print(f'Layer2 (軽微な事故): {L2:5d}件  [{",".join(sorted(LAYER2_EXACT)[:4])}...]')
    print(f'Layer3 (ヒヤリハット):{L3:5d}件  [日常操作全般]')
    print(f'合計:                {total:5d}件')
    print()
    print(f'実測比率: 1 : {r2} : {r3}')
    print(f'理論比率: 1 : 29  : 300')
    print(f'Layer2捕捉率: {g2}%  (理論の{g2}%)')
    print(f'Layer3捕捉率: {g3}%  (理論の{g3}%)')
    print(f'未捕捉推定:   {missing}件')
    print()
    print('【洞察】')
    print('  Layer2が少ない = 軽微事故の記録経路が不足')
    print('  またか！ボタン活用 → Layer2増加 → 比率が理論値に近づく')
    print('  これがMoCKA制度成熟の定量的証明になる')
    print()
    print('Layer1サンプル:')
    for s in buckets[1][:5]:
        print(f"  [{s['what_type']:20s}] {s['title'][:35]}")
    print()
    print('Layer2サンプル:')
    for s in buckets[2][:5]:
        print(f"  [{s['what_type']:20s}] {s['title'][:35]}")
    print('='*55)
    return report

if __name__ == '__main__':
    run()
