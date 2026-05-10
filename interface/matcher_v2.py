# -*- coding: utf-8 -*-
"""
MoCKA Language Matcher v2.0
5W1H構造照合エンジン

text_to_5w1h.parse() で構造分解 →
events.dbを5W1H軸の組み合わせで照合 →
recurrence_flag / incident_flag で成功/失敗判定

v1との違い:
  単語出現率照合 → 5W1H組み合わせ照合
  「PowerShell × 編集 × Claude」= 過去何回問題になったか
"""
import sqlite3, sys, json, importlib.util
from pathlib import Path
from datetime import datetime
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

BASE    = Path(r'C:\Users\sirok\MoCKA')
DB_PATH = BASE / 'data' / 'mocka_events.db'
PARSER  = BASE / 'interface' / 'text_to_5w1h.py'

# text_to_5w1h を動的import
spec = importlib.util.spec_from_file_location("text_to_5w1h", PARSER)
mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
parse_5w1h = mod.parse

# ===== 照合戦略 =====
# 5W1H組み合わせの優先順位（高いほど信頼性高い）
MATCH_STRATEGIES = [
    # (戦略名, カラム組み合わせ, 重み)
    ('WHO+HOW+WHAT', ['who_actor','how_trigger','what_type'], 1.0),
    ('WHO+HOW',      ['who_actor','how_trigger'],             0.8),
    ('WHO+WHAT',     ['who_actor','what_type'],               0.7),
    ('HOW+WHAT',     ['how_trigger','what_type'],             0.7),
    ('HOW+WHERE',    ['how_trigger','where_component'],       0.6),
    ('WHO+WHERE',    ['who_actor','where_component'],         0.5),
    ('HOW_only',     ['how_trigger'],                         0.4),
    ('WHO_only',     ['who_actor'],                           0.3),
]

def build_query(w5h1, cols):
    """5W1H値とカラムリストからSQLを構築"""
    col_map = {
        'who_actor':       w5h1.get('who'),
        'what_type':       w5h1.get('what'),
        'where_component': w5h1.get('where'),
        'why_purpose':     w5h1.get('why'),
        'how_trigger':     w5h1.get('how'),
    }
    conditions = []
    params = []
    for col in cols:
        val = col_map.get(col)
        if val:
            conditions.append(f"{col} LIKE ?")
            params.append(f'%{val}%')
    if not conditions:
        return None, []
    sql = f"""
        SELECT event_id, when_ts, who_actor, what_type,
               where_component, why_purpose, how_trigger,
               recurrence_flag, pattern_score, free_note
        FROM events
        WHERE {' AND '.join(conditions)}
        LIMIT 100
    """
    return sql, params

def judge_event(row):
    """イベント1件をSUCCESS/DANGER/NEUTRALに判定"""
    SUCCESS_W = {'完了','成功','確認','稼働','達成','解決','修正済','正常','ok','done','fixed'}
    DANGER_W  = {'エラー','失敗','再発','インシデント','問題','バグ','文字化け',
                 'critical','danger','error','broken','停止','violation','指摘','却下'}

    full = ' '.join(filter(None,[
        str(row[3] or ''), str(row[5] or ''),
        str(row[6] or ''), str(row[9] or '')
    ])).lower()

    recur = row[7] or 0
    if recur:
        return 'DANGER', 1.2  # 再発フラグは強いDANGER

    d_score = sum(1 for w in DANGER_W  if w in full)
    s_score = sum(1 for w in SUCCESS_W if w in full)

    if d_score > s_score:   return 'DANGER',  d_score
    if s_score > d_score:   return 'SUCCESS', s_score
    return 'NEUTRAL', 0

def match_5w1h(text, top_n=3, verbose=True):
    """
    メイン照合関数
    1. text → 5W1H分解
    2. 5W1H組み合わせでevents.db照合
    3. 成功/失敗判定 + スコア算出
    """
    # Step1: 5W1H分解
    w5h1 = parse_5w1h(text, verbose=False)

    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    # Step2: 戦略順に照合
    all_hits   = {}   # event_id → {score, verdict, row, strategy}
    strategy_results = []

    for strategy_name, cols, weight in MATCH_STRATEGIES:
        sql, params = build_query(w5h1, cols)
        if not sql or not params:
            continue
        try:
            rows = cur.execute(sql, params).fetchall()
        except Exception as e:
            continue

        if not rows:
            continue

        s_count = d_count = n_count = 0
        for row in rows:
            eid = row[0]
            verdict, strength = judge_event(row)
            score = weight * (1 + strength * 0.1)

            if eid not in all_hits or all_hits[eid]['score'] < score:
                all_hits[eid] = {
                    'score':    round(score, 3),
                    'verdict':  verdict,
                    'strategy': strategy_name,
                    'when':     str(row[1] or '')[:10],
                    'who':      str(row[2] or '')[:20],
                    'what':     str(row[3] or '')[:30],
                    'why':      str(row[5] or '')[:80],
                    'how':      str(row[6] or '')[:50],
                    'recur':    row[7] or 0,
                }
            if verdict == 'SUCCESS': s_count += 1
            elif verdict == 'DANGER': d_count += 1
            else: n_count += 1

        strategy_results.append({
            'strategy': strategy_name,
            'hits':     len(rows),
            'success':  s_count,
            'danger':   d_count,
            'weight':   weight,
        })

    conn.close()

    if not all_hits:
        result = {
            'verdict': 'UNKNOWN', 'score': 0,
            'success_rate': 0, 'danger_rate': 0,
            'w5h1': w5h1, 'hits': 0, 'top_events': [],
        }
        if verbose:
            print(f"\n⚪ UNKNOWN — events.dbに類似パターンなし")
            print(f"   5W1H: {w5h1}")
        return result

    # Step3: 全ヒットを集計
    total = len(all_hits)
    s_total = sum(1 for v in all_hits.values() if v['verdict']=='SUCCESS')
    d_total = sum(1 for v in all_hits.values() if v['verdict']=='DANGER')
    success_rate = s_total / total
    danger_rate  = d_total / total

    # スコア上位を取得
    sorted_hits = sorted(all_hits.values(), key=lambda x: x['score'], reverse=True)
    top_events  = sorted_hits[:top_n]

    # 最終判定
    # 再発フラグ付きDANGERが1件でもあれば即DANGER
    has_recur = any(v['recur'] for v in all_hits.values())
    if has_recur or danger_rate > 0.45:
        verdict = 'DANGER'
    elif success_rate > 0.50:
        verdict = 'SUCCESS'
    else:
        verdict = 'NEUTRAL'

    final_score = round(danger_rate - success_rate, 3)

    result = {
        'verdict':      verdict,
        'score':        final_score,
        'success_rate': round(success_rate, 3),
        'danger_rate':  round(danger_rate, 3),
        'hits':         total,
        'has_recur':    has_recur,
        'w5h1':         w5h1,
        'top_events':   top_events,
        'strategies':   strategy_results,
    }

    if verbose:
        mark = {'DANGER':'🔴','SUCCESS':'🟢','NEUTRAL':'⚪','UNKNOWN':'❓'}.get(verdict,'❓')
        print(f"\n{'='*65}")
        print(f"【Language Matcher v2.0 — 5W1H構造照合】")
        print(f"{'='*65}")
        print(f"入力: {text}")
        print(f"{'─'*65}")
        print(f"5W1H分解:")
        print(f"  WHO={w5h1.get('who')}  WHAT={w5h1.get('what')}  WHERE={w5h1.get('where')}")
        print(f"  HOW={w5h1.get('how')}  WHY={w5h1.get('why')}")
        print(f"{'─'*65}")
        print(f"照合結果: {total}件ヒット")
        for sr in strategy_results:
            if sr['hits'] > 0:
                print(f"  [{sr['strategy']}] {sr['hits']}件 "
                      f"(S:{sr['success']} D:{sr['danger']})")
        print(f"{'─'*65}")
        print(f"判定: {mark} {verdict}  score={final_score:+.3f}")
        print(f"  SUCCESS率:{success_rate:.1%}  DANGER率:{danger_rate:.1%}"
              f"  再発フラグ:{has_recur}")
        print(f"\n--- 類似イベント TOP{top_n} ---")
        for i, ev in enumerate(top_events, 1):
            m = {'DANGER':'🔴','SUCCESS':'🟢','NEUTRAL':'⚪'}.get(ev['verdict'],'⚪')
            print(f"{i}. {m} [{ev['when']}] {ev['strategy']} score={ev['score']}")
            print(f"   why: {ev['why'][:70]}")
            print(f"   how: {ev['how'][:50]}  recur:{ev['recur']}")
        print(f"{'='*65}")

    return result


if __name__ == '__main__':
    if len(sys.argv) > 1:
        match_5w1h(' '.join(sys.argv[1:]))
    else:
        tests = [
            "PowerShellでファイルを編集します",
            "Pythonスクリプトで修正完了しました",
            "文字化けが発生してエラーになりました",
            "ClaudeがMCPでevents.dbにイベントを記録します",
            "きむら博士がPowerShellではなくPythonで書き直すよう指摘した",
        ]
        for t in tests:
            match_5w1h(t)
            print()
