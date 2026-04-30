# -*- coding: utf-8 -*-
"""MoCKA Heinrich Engine v3 - 最適分類"""
import json, sqlite3, sys, datetime, re
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

BASE    = Path(r'C:\Users\sirok\MoCKA')
DB_PATH = BASE / 'data' / 'mocka_events.db'
OUT     = BASE / 'data' / 'heinrich_report.json'

# ===== Layer1: 重大事故 =====
# AI/システムの意図的違反・データ破壊・制度違反・セキュリティ侵害
LAYER1_EXACT_TYPES = {
    'MATAKA', 'CLAIM', 'INTEGRITY_VIOLATION', 'CRITICAL',
    'INSTRUCTION_IGNORE', 'DEPENDENCY_BREAK', 'FAST_WRONG',
    'ai_violation', 'governance_degradation', 'AUDIT_VIOLATION'
}
LAYER1_KW_STRONG = [
    # AI違反
    'fabricat', 'unauthorized', 'overwrite', 'violation', 'ai_violation',
    'integrity', '捏造', '無断', '上書き', '権限', 'permission',
    # データ破壊
    'corruption', 'destroy', 'delete_all', 'drop_table',
    # 制度違反
    'constitution_breach', 'rule_break', 'policy_violation',
    # セキュリティ
    'leak', 'exposure', 'credential', 'token_exposed'
]

# ===== Layer2: 軽微な事故 =====
# エラー・失敗・再発・クレーム・警告・ドリフト
LAYER2_EXACT_TYPES = {
    'DANGER', 'ERROR', 'INCIDENT', 'recurrence',
    'SLOW_DRIFT', 'FORMAT_COLLAPSE', 'WARNING_EVENT',
    'MATAKA_AUTO', 'MORPHO_DANGER'
}
LAYER2_KW = [
    # エラー系
    'error', 'exception', 'fail', 'timeout', 'broken',
    'エラー', '失敗', 'バグ', 'bug', 'invalid',
    # 再発系
    'また', '再発', 'recur', 'repeat', '繰り返し',
    # 否定・問題
    '問題', '誤って', 'できない', '動かない', '止まった',
    '違う', 'ちがう', 'おかしい', 'wrong', 'incorrect',
    # 認知的問題
    'なぜ', 'どうして', '意味がわからん', 'わからない',
    # ドリフト
    'drift', 'collapse', 'degradation', 'decline'
]
# Layer2除外: これらはLayer3
LAYER2_EXCLUDE_TYPES = {
    'save', 'collaboration', 'share', 'record', 'broadcast',
    'process', 'storage', 'essence_update', 'claude_mcp',
    'collect', 'success_hint', 'success_great', 'playwright_capture'
}

# ===== Layer3: ヒヤリハット =====
# 日常操作・記録・収集・AIとの通常インタラクション
LAYER3_EXACT_TYPES = {
    'save', 'collaboration', 'share', 'record', 'broadcast',
    'process', 'storage', 'essence_update', 'claude_mcp',
    'collect', 'success_hint', 'success_great',
    'playwright_capture',  # 通常の画面キャプチャ
    'DECISION_APPROVED', 'DECISION_REJECTED',
    'AUTO_GATE_APPROVED', 'AUDIT_COMPLETE'
}
LAYER3_KW = [
    'hint', 'check', '確認', '一応', '念のため',
    'ちょっと', '少し', 'かも', 'maybe', 'perhaps'
]

def classify(row):
    wt  = str(row['what_type'] or '').strip()
    wtu = wt.upper()
    title = str(row['title'] or '').lower()
    why   = str(row['why_purpose'] or '').lower()
    free  = str(row['free_note'] or '').lower()
    full  = ' '.join([wt, title, why, free])

    # Layer1: 厳密な違反・重大事故
    if wt in LAYER1_EXACT_TYPES:
        return 1
    if any(k in full for k in LAYER1_KW_STRONG):
        # playwright_captureはLayer1除外（通常キャプチャ）
        if wt == 'playwright_capture':
            return 3
        return 1

    # Layer2: エラー・失敗・再発（ただしLayer2除外タイプは除く）
    if wt in LAYER2_EXACT_TYPES and wt not in LAYER2_EXCLUDE_TYPES:
        return 2
    if wt not in LAYER3_EXACT_TYPES and any(k in full for k in LAYER2_KW):
        return 2

    # Layer3: 日常操作・観測価値のあるヒヤリハット
    return 3

def run():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("""
        SELECT event_id, what_type, title, why_purpose,
               how_trigger, free_note, when_ts
        FROM events
    """)
    rows = cur.fetchall()
    con.close()

    buckets = {1: [], 2: [], 3: []}
    type_stats = {}

    for row in rows:
        layer = classify(row)
        wt = str(row['what_type'] or '')
        type_stats[wt] = type_stats.get(wt, {'l1':0,'l2':0,'l3':0})
        type_stats[wt]['l'+str(layer)] += 1
        buckets[layer].append({
            'event_id':  row['event_id'],
            'what_type': row['what_type'],
            'title':     (row['title'] or '')[:60],
            'when':      row['when_ts']
        })

    L1, L2, L3 = len(buckets[1]), len(buckets[2]), len(buckets[3])
    total = L1 + L2 + L3

    r2 = round(L2/L1, 1) if L1 > 0 else 0
    r3 = round(L3/L1, 1) if L1 > 0 else 0
    g2 = round((r2/29)*100,  1) if L1 > 0 else 0
    g3 = round((r3/300)*100, 1) if L1 > 0 else 0

    report = {
        'generated_at': datetime.datetime.now().isoformat(),
        'total_events': total,
        'heinrich': {
            'layer1_critical':  {'count': L1, 'theory': 1,   'label': 'Critical/重大事故'},
            'layer2_minor':     {'count': L2, 'theory': 29,  'label': 'Minor/軽微な事故'},
            'layer3_near_miss': {'count': L3, 'theory': 300, 'label': 'Near-miss/ヒヤリハット'},
            'actual_ratio':  f'1:{r2}:{r3}',
            'theory_ratio':  '1:29:300',
            'capture_rate': {
                'layer2': f'{g2}%',
                'layer3': f'{g3}%',
                'interpretation': 'MoCKAが捕捉できている事案の割合'
            },
            'missing_estimate': max(0, int(L1*300 - L3))
        },
        'layer1_samples': buckets[1][:10],
        'layer2_samples': buckets[2][:10],
        'layer3_samples': buckets[3][:10],
        'type_distribution': dict(
            sorted(type_stats.items(), key=lambda x: -(x[1]['l1']+x[1]['l2']+x[1]['l3']))[:20]
        )
    }

    json.dump(report, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    print('='*50)
    print('MoCKA Heinrich Engine v3')
    print('='*50)
    print(f'Layer1 (重大):   {L1:4d}件')
    print(f'Layer2 (軽微):   {L2:4d}件')
    print(f'Layer3 (ヒヤリ): {L3:4d}件')
    print(f'合計:            {total:4d}件')
    print(f'実測比率: 1:{r2}:{r3}')
    print(f'理論比率: 1:29:300')
    print(f'Layer2捕捉率: {g2}%')
    print(f'Layer3捕捉率: {g3}%')
    print(f'未捕捉推定: {max(0,int(L1*300-L3))}件')
    print()
    print('Layer1サンプル（重大事故）:')
    for s in buckets[1][:5]:
        print(f"  [{s['what_type']}] {s['title'][:40]}")
    print()
    print('Layer2サンプル（軽微事故）:')
    for s in buckets[2][:5]:
        print(f"  [{s['what_type']}] {s['title'][:40]}")
    print('='*50)
    return report

if __name__ == '__main__':
    run()
