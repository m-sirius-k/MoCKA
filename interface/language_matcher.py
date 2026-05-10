# -*- coding: utf-8 -*-
"""
MoCKA Language Matcher v1.0
言語出現率照合エンジン — Layer 1

入力テキスト → 形態素分解 → events.db全文照合
→ SUCCESS率/DANGER率 + 類似イベントTOP3を返す

使い方:
  python language_matcher.py "テキストをここに入れる"
  または import して match(text) を呼ぶ
"""
import sqlite3, sys, json, re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

BASE    = Path(r'C:\Users\sirok\MoCKA')
DB_PATH = BASE / 'data' / 'mocka_events.db'

# 照合対象カラム（充足率97%以上）と重み
SEARCH_COLS = [
    ('why_purpose',  0.35),  # 目的軸 — 最重要
    ('how_trigger',  0.30),  # 手順軸
    ('free_note',    0.20),  # 文脈軸
    ('who_actor',    0.10),  # 主体軸
    ('what_type',    0.05),  # 種別軸
]

# 成功/失敗判定キーワード
SUCCESS_WORDS = {
    '完了','成功','確認','稼働','達成','解決','修正済','グレート',
    'ok','passed','done','fixed','完成','正常','動作'
}
DANGER_WORDS = {
    'エラー','失敗','再発','インシデント','問題','バグ','文字化け',
    'critical','danger','error','broken','停止','崩壊','violation'
}

def tokenize(text):
    """Janomeで形態素分解 → 意味語のみ返す"""
    try:
        from janome.tokenizer import Tokenizer
        t = Tokenizer()
        VALID_POS = {'名詞','動詞','形容詞','副詞'}
        SKIP = {'を','は','が','に','で','と','も','の','へ','から',
                'まで','より','など','ね','よ','さ','れ','た','て',
                'し','い','な','だ','です','ます','ない','する','ある',
                'いる','なる','れる','られる','せる','させる'}
        tokens = []
        for tok in t.tokenize(text):
            pos = tok.part_of_speech.split(',')[0]
            surface = tok.surface.strip()
            base = tok.base_form.strip()
            if (pos in VALID_POS and 
                surface not in SKIP and 
                base not in SKIP and
                len(surface) > 1):
                tokens.append(surface)
                if base != surface and len(base) > 1:
                    tokens.append(base)
        return list(set(tokens))
    except ImportError:
        # Janome未インストール時は単純分割
        words = re.findall(r'[ぁ-んァ-ン一-龥a-zA-Z]{2,}', text)
        return list(set(words))

def match(text, top_n=3, verbose=True):
    """
    テキストをevents.dbと照合してスコアを返す
    
    Returns:
        dict: {
            'score': float,        # 総合スコア(0-1)
            'success_rate': float,
            'danger_rate': float,
            'tokens': list,        # 抽出トークン
            'hits': int,           # ヒットイベント数
            'top_events': list,    # 類似イベントTOP3
            'verdict': str,        # SUCCESS/DANGER/NEUTRAL
        }
    """
    tokens = tokenize(text)
    if not tokens:
        return {'score': 0, 'verdict': 'NEUTRAL', 'tokens': [], 'hits': 0}

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 各トークンでイベントを検索
    event_scores = defaultdict(float)
    event_data = {}

    for token in tokens:
        for col, weight in SEARCH_COLS:
            try:
                rows = cur.execute(f"""
                    SELECT event_id, when_ts, what_type, why_purpose, 
                           how_trigger, free_note, recurrence_flag, pattern_score
                    FROM events 
                    WHERE {col} LIKE ?
                    LIMIT 50
                """, (f'%{token}%',)).fetchall()
                
                for row in rows:
                    eid = row['event_id']
                    event_scores[eid] += weight
                    if eid not in event_data:
                        event_data[eid] = dict(row)
                        event_data[eid]['matched_tokens'] = []
                    event_data[eid]['matched_tokens'].append(f"{token}@{col}")
            except Exception as e:
                pass

    conn.close()

    if not event_scores:
        return {
            'score': 0, 'verdict': 'NEUTRAL', 'tokens': tokens,
            'hits': 0, 'success_rate': 0, 'danger_rate': 0, 'top_events': []
        }

    # スコア上位イベントを取得
    sorted_events = sorted(event_scores.items(), key=lambda x: x[1], reverse=True)
    top_event_ids = [e[0] for e in sorted_events[:top_n*3]]

    # SUCCESS/DANGER判定
    success_count = 0
    danger_count = 0
    top_events = []

    for eid, score in sorted_events[:top_n*3]:
        ev = event_data[eid]
        # イベント全テキストを結合して判定
        full_text = ' '.join(filter(None, [
            str(ev.get('what_type','')),
            str(ev.get('why_purpose','')),
            str(ev.get('how_trigger','')),
            str(ev.get('free_note',''))
        ])).lower()
        
        is_success = any(w in full_text for w in SUCCESS_WORDS)
        is_danger  = any(w in full_text for w in DANGER_WORDS)
        is_recur   = ev.get('recurrence_flag', 0)
        
        if is_danger or is_recur:
            danger_count += 1
        elif is_success:
            success_count += 1

        if len(top_events) < top_n:
            top_events.append({
                'event_id': eid,
                'when': str(ev.get('when_ts',''))[:10],
                'why': str(ev.get('why_purpose',''))[:80],
                'how': str(ev.get('how_trigger',''))[:60],
                'recurrence': bool(is_recur),
                'match_score': round(score, 3),
                'matched': ev.get('matched_tokens', [])[:3],
                'verdict': 'DANGER' if (is_danger or is_recur) else ('SUCCESS' if is_success else 'NEUTRAL'),
            })

    total_checked = min(len(sorted_events), top_n*3)
    success_rate = success_count / total_checked if total_checked else 0
    danger_rate  = danger_count  / total_checked if total_checked else 0

    # 総合スコアと判定
    score = danger_rate - success_rate  # -1(完全成功) 〜 +1(完全危険)
    if danger_rate > 0.4:
        verdict = 'DANGER'
    elif success_rate > 0.4:
        verdict = 'SUCCESS'
    else:
        verdict = 'NEUTRAL'

    result = {
        'score':        round(score, 3),
        'success_rate': round(success_rate, 3),
        'danger_rate':  round(danger_rate, 3),
        'tokens':       tokens,
        'hits':         len(event_scores),
        'top_events':   top_events,
        'verdict':      verdict,
        'analyzed_at':  datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
    }

    if verbose:
        print(f"\n{'='*60}")
        print(f"【Language Matcher v1.0】")
        print(f"{'='*60}")
        print(f"入力: {text[:80]}")
        print(f"トークン({len(tokens)}個): {tokens[:10]}")
        print(f"ヒット件数: {len(event_scores)} / 7,955件")
        print(f"判定: {verdict}  score={score:+.3f}")
        print(f"  SUCCESS率: {success_rate:.1%}  DANGER率: {danger_rate:.1%}")
        print(f"\n--- 類似イベント TOP{top_n} ---")
        for i, ev in enumerate(top_events, 1):
            mark = '🔴' if ev['verdict']=='DANGER' else ('🟢' if ev['verdict']=='SUCCESS' else '⚪')
            print(f"{i}. {mark} [{ev['when']}] score={ev['match_score']}")
            print(f"   why: {ev['why'][:70]}")
            print(f"   matched: {ev['matched'][:3]}")
        print(f"{'='*60}")

    return result

# ============================================================
# テスト実行
# ============================================================
if __name__ == '__main__':
    if len(sys.argv) > 1:
        text = ' '.join(sys.argv[1:])
        match(text)
    else:
        # デフォルトテスト4件
        tests = [
            "PowerShellでファイルを編集します",           # → DANGER期待（禁止パターン）
            "Pythonスクリプトで修正完了しました",          # → SUCCESS期待
            "文字化けが発生してエラーになりました",        # → DANGER期待
            "essenceをPHLとして注入して次のセッションに引き継ぐ",  # → NEUTRAL期待
        ]
        print("【自動テスト 4件】")
        for t in tests:
            r = match(t, verbose=True)
            print()
