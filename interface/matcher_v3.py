# -*- coding: utf-8 -*-
"""
MoCKA Language Matcher v3.0
きむら博士の発言文脈照合エンジン

核心設計:
  free_noteに蓄積された「きむら博士の否定・指摘・承認語」を軸に照合
  5W1H分解 + free_note全文検索 + 文脈スコアリング
"""
import sqlite3, sys, json, importlib.util
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

BASE    = Path(r'C:\Users\sirok\MoCKA')
DB_PATH = BASE / 'data' / 'mocka_events.db'
PARSER  = BASE / 'interface' / 'text_to_5w1h.py'

spec = importlib.util.spec_from_file_location("text_to_5w1h", PARSER)
mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
parse_5w1h = mod.parse

# ===== きむら博士の発言パターン =====
KIMURA_DANGER = [
    'powershell以外', 'なぜ', 'いや', 'いやいや', '違う', 'そうじゃない',
    '指摘', 'またか', 'また同じ', '文字化け', '再発', '問題は',
    'おかしい', 'ダメ', 'なんで', 'どうして', 'スルー',
    'エラー', '失敗', '崩れ', '止まっ',
]
KIMURA_SUCCESS = [
    'グレート', 'そこです', 'ヒント', '採用', '確定', '完璧',
    'いいね', 'その通り', 'なるほど', '正しい', 'ok',
    'できた', '動いた', '成功', '完了',
]

# ===== 照合関数 =====
def search_free_note(cur, keywords, limit=30):
    """free_noteからキーワード群でイベントを検索"""
    hits = {}
    for kw in keywords:
        try:
            rows = cur.execute("""
                SELECT event_id, when_ts, who_actor, what_type,
                       why_purpose, how_trigger, free_note,
                       recurrence_flag, pattern_score
                FROM events
                WHERE free_note LIKE ?
                LIMIT ?
            """, (f'%{kw}%', limit)).fetchall()
            for row in rows:
                eid = row[0]
                if eid not in hits:
                    hits[eid] = {
                        'row': row,
                        'matched_kw': [],
                        'score': 0,
                    }
                hits[eid]['matched_kw'].append(kw)
                hits[eid]['score'] += 1
        except:
            pass
    return hits

def match_v3(text, top_n=3, verbose=True):
    """
    v3メイン照合
    1. 入力テキストを5W1H分解
    2. 入力テキスト内のきむら博士パターンを検出
    3. free_noteで文脈照合
    4. recurrence_flag + 文脈スコアで判定
    """
    w5h1 = parse_5w1h(text, verbose=False)

    # 入力テキスト内のパターン検出
    text_danger  = [kw for kw in KIMURA_DANGER  if kw in text]
    text_success = [kw for kw in KIMURA_SUCCESS if kw in text]

    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    # 照合キーワードを構築
    # 入力の5W1H値 + 入力内の信号語 + HOW値
    search_kw_danger  = list(set(text_danger))
    search_kw_success = list(set(text_success))

    # HOW/WHEREの値も検索対象に
    if w5h1.get('how'):
        search_kw_danger.append(w5h1['how'].replace('_',' ').split('_')[0])
    if w5h1.get('where') and w5h1['where'] not in ('Python','PowerShell'):
        search_kw_danger.append(w5h1['where'])

    # 入力にDANGER語がなければ、WHATやHOWで文脈照合
    if not search_kw_danger:
        if w5h1.get('what'):
            search_kw_danger.append(w5h1['what'])
        if w5h1.get('how'):
            search_kw_danger.append(str(w5h1['how'])[:10])

    # free_note照合
    danger_hits  = search_free_note(cur, search_kw_danger)  if search_kw_danger  else {}
    success_hits = search_free_note(cur, search_kw_success) if search_kw_success else {}

    # recurrence_flagで重み付け
    recur_count = 0
    for eid, h in danger_hits.items():
        row = h['row']
        if row[7]:  # recurrence_flag
            h['score'] += 2
            recur_count += 1

    conn.close()

    total_danger  = len(danger_hits)
    total_success = len(success_hits)
    total = total_danger + total_success

    # 判定
    has_recur = recur_count > 0
    if has_recur or (total_danger > 0 and total_danger > total_success * 1.5):
        verdict = 'DANGER'
    elif total_success > total_danger * 1.5:
        verdict = 'SUCCESS'
    elif text_danger:
        verdict = 'DANGER'
    elif text_success:
        verdict = 'SUCCESS'
    else:
        verdict = 'NEUTRAL'

    danger_rate  = total_danger  / total if total else 0
    success_rate = total_success / total if total else 0
    score = round(danger_rate - success_rate, 3)

    # TOP3イベント
    top_danger  = sorted(danger_hits.values(),  key=lambda x: x['score'], reverse=True)[:top_n]
    top_success = sorted(success_hits.values(), key=lambda x: x['score'], reverse=True)[:top_n]

    def fmt_event(h, verdict):
        row = h['row']
        return {
            'verdict':  verdict,
            'when':     str(row[1] or '')[:10],
            'why':      str(row[4] or '')[:80],
            'how':      str(row[5] or '')[:60],
            'note':     str(row[6] or '')[:100],
            'recur':    row[7] or 0,
            'matched':  h['matched_kw'][:3],
            'score':    h['score'],
        }

    top_events = (
        [fmt_event(h,'DANGER')  for h in top_danger[:2]] +
        [fmt_event(h,'SUCCESS') for h in top_success[:1]]
    )

    result = {
        'verdict':       verdict,
        'score':         score,
        'danger_rate':   round(danger_rate, 3),
        'success_rate':  round(success_rate, 3),
        'danger_hits':   total_danger,
        'success_hits':  total_success,
        'has_recur':     has_recur,
        'recur_count':   recur_count,
        'text_danger':   text_danger,
        'text_success':  text_success,
        'search_kw':     search_kw_danger,
        'w5h1':          w5h1,
        'top_events':    top_events,
    }

    if verbose:
        mark = {'DANGER':'🔴','SUCCESS':'🟢','NEUTRAL':'⚪'}.get(verdict,'❓')
        print(f"\n{'='*65}")
        print(f"【Language Matcher v3.0 — きむら博士文脈照合】")
        print(f"{'='*65}")
        print(f"入力: {text}")
        print(f"{'─'*65}")
        print(f"5W1H: WHO={w5h1.get('who')}  HOW={w5h1.get('how')}  WHAT={w5h1.get('what')}")
        print(f"入力内DANGER語: {text_danger}")
        print(f"入力内SUCCESS語: {text_success}")
        print(f"照合キーワード: {search_kw_danger}")
        print(f"{'─'*65}")
        print(f"DANGER文脈: {total_danger}件  SUCCESS文脈: {total_success}件")
        print(f"再発フラグ付き: {recur_count}件")
        print(f"{'─'*65}")
        print(f"判定: {mark} {verdict}  score={score:+.3f}")
        print(f"\n--- 関連イベント ---")
        for ev in top_events:
            m = {'DANGER':'🔴','SUCCESS':'🟢'}.get(ev['verdict'],'⚪')
            print(f"{m} [{ev['when']}] matched={ev['matched']} recur={ev['recur']}")
            print(f"   why: {ev['why'][:70]}")
            if ev['note']:
                print(f"   note: {ev['note'][:80]}")
        print(f"{'='*65}")

    return result


if __name__ == '__main__':
    if len(sys.argv) > 1:
        match_v3(' '.join(sys.argv[1:]))
    else:
        tests = [
            "PowerShellでファイルを編集します",
            "Pythonスクリプトで修正完了しました",
            "文字化けが発生してエラーになりました",
            "なぜPowerShellで書いているんですか",
            "グレートです、Pythonスクリプトで完璧に動きました",
        ]
        for t in tests:
            match_v3(t)
            print()
