# -*- coding: utf-8 -*-
"""
MoCKA Morphology Engine v1.0
形態素解析 + 組み合わせ出現確率エンジン
AYX+TS理論実装: ゴールは固定点ではなく連続進行する変化軸の中にある

処理フロー:
1. テキストを形態素解析(Janome)で分解
2. 品詞フィルタリング(主語/述語/動詞/形容詞/名詞)
3. N-gram組み合わせ生成
4. 過去の失敗事例(Layer1/Layer2)との照合
5. 出現確率を算出 -> 閾値超でDANGER警告
"""
import json, sqlite3, sys, datetime, itertools
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

BASE    = Path(r'C:\Users\sirok\MoCKA')
DB_PATH = BASE / 'data' / 'mocka_events.db'
PATTERN_DB = BASE / 'data' / 'morphology_patterns.db'
HEINRICH = BASE / 'data' / 'heinrich_report.json'

# ===== 品詞フィルタ =====
# 意味を持つ品詞のみ抽出(助詞・助動詞・記号を除外)
VALID_POS = {
    '名詞', '動詞', '形容詞', '副詞', '感動詞'
}
INVALID_SURFACE = {
    'を', 'は', 'が', 'に', 'で', 'と', 'も', 'の', 'へ',
    'から', 'まで', 'より', 'など', 'ね', 'よ', 'さ', 'れ', 'た',
    'て', 'し', 'い', 'な', 'だ', 'です', 'ます', 'ない'
}

def tokenize(text):
    """Janomeで形態素解析 -> 意味のある品詞のみ返す"""
    try:
        from janome.tokenizer import Tokenizer
        t = Tokenizer()
        tokens = []
        for tok in t.tokenize(text):
            pos = tok.part_of_speech.split(',')[0]
            surface = tok.surface.lower()
            if pos in VALID_POS and surface not in INVALID_SURFACE and len(surface) > 1:
                tokens.append({
                    'surface': surface,
                    'pos': pos,
                    'base': tok.base_form.lower()
                })
        return tokens
    except Exception as e:
        print(f'tokenize error: {e}')
        return []

def generate_ngrams(tokens, n=2):
    """N-gram組み合わせ生成(2-gram + 3-gram)"""
    surfaces = [t['surface'] for t in tokens]
    ngrams = []
    for size in range(2, n+2):
        for i in range(len(surfaces) - size + 1):
            ngrams.append(tuple(surfaces[i:i+size]))
    return ngrams

def init_pattern_db():
    """パターンDBを初期化"""
    con = sqlite3.connect(PATTERN_DB)
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ngram TEXT NOT NULL,
        layer INTEGER NOT NULL,
        event_id TEXT,
        source TEXT,
        count INTEGER DEFAULT 1,
        last_seen TEXT,
        UNIQUE(ngram, layer)
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,
        tokens TEXT,
        danger_score REAL,
        matched_patterns TEXT,
        prediction TEXT,
        created_at TEXT
    )''')
    con.commit()
    con.close()
    print('morphology_patterns.db 初期化完了')

def build_pattern_library():
    """
    events.dbのLayer1/Layer2イベントから
    失敗パターンのN-gram辞書を構築
    """
    # ハインリッヒレポートから Layer1/Layer2サンプル取得
    heinrich = json.load(open(HEINRICH, encoding='utf-8'))
    layer1_ids = {s['event_id'] for s in heinrich['heinrich']['layer1_critical'].get('samples', []) 
                  if isinstance(heinrich['heinrich']['layer1_critical'], dict) and 'samples' in heinrich['heinrich']['layer1_critical']}

    # events.dbから全Layer1/Layer2テキストを取得
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # Layer1: 重大事故
    layer1_types = ('MATAKA', 'CLAIM', 'INTEGRITY_VIOLATION', 'CRITICAL', 'INSTRUCTION_IGNORE')
    placeholders = ','.join('?' * len(layer1_types))
    cur.execute(f"SELECT event_id, what_type, title, why_purpose FROM events WHERE what_type IN ({placeholders})", layer1_types)
    layer1_rows = cur.fetchall()

    # Layer2: 軽微な事故
    layer2_keywords = ['error', 'fail', 'timeout', 'exception']
    cur.execute("SELECT event_id, what_type, title, why_purpose FROM events WHERE what_type IN ('DANGER','ERROR','INCIDENT','recurrence')")
    layer2_rows = cur.fetchall()
    con.close()

    # パターンDB構築
    pcon = sqlite3.connect(PATTERN_DB)
    pcur = pcon.cursor()
    now = datetime.datetime.now().isoformat()

    l1_patterns = 0
    l2_patterns = 0

    for rows, layer in [(layer1_rows, 1), (layer2_rows, 2)]:
        for row in rows:
            event_id, what_type, title, why = row
            text = ' '.join(filter(None, [title, why]))
            if not text or len(text) < 3:
                continue
            tokens = tokenize(text)
            if not tokens:
                continue
            ngrams = generate_ngrams(tokens, n=3)
            for ng in ngrams:
                ng_str = '|'.join(ng)
                try:
                    pcur.execute('''INSERT INTO patterns(ngram, layer, event_id, source, count, last_seen)
                                   VALUES(?,?,?,?,1,?)
                                   ON CONFLICT(ngram, layer) DO UPDATE SET
                                   count=count+1, last_seen=?''',
                                (ng_str, layer, event_id, what_type, now, now))
                    if layer == 1:
                        l1_patterns += 1
                    else:
                        l2_patterns += 1
                except Exception as e:
                    pass

    pcon.commit()
    pcon.close()
    print(f'Layer1パターン登録: {l1_patterns}件')
    print(f'Layer2パターン登録: {l2_patterns}件')

def predict(text, threshold=0.3):
    """
    入力テキストを解析して失敗経路への進入確率を返す
    threshold: 0.0-1.0 (この値を超えるとDANGER)
    """
    tokens = tokenize(text)
    if not tokens:
        return {'danger_score': 0.0, 'prediction': 'SAFE', 'matched': []}

    ngrams = generate_ngrams(tokens, n=3)
    if not ngrams:
        return {'danger_score': 0.0, 'prediction': 'SAFE', 'matched': []}

    pcon = sqlite3.connect(PATTERN_DB)
    pcur = pcon.cursor()

    matched_l1 = []
    matched_l2 = []

    for ng in ngrams:
        ng_str = '|'.join(ng)
        # Layer1マッチ(重大事故パターン)
        pcur.execute('SELECT ngram, count FROM patterns WHERE ngram=? AND layer=1', (ng_str,))
        row = pcur.fetchone()
        if row:
            matched_l1.append({'pattern': ng_str, 'count': row[1]})
        # Layer2マッチ(軽微事故パターン)
        pcur.execute('SELECT ngram, count FROM patterns WHERE ngram=? AND layer=2', (ng_str,))
        row = pcur.fetchone()
        if row:
            matched_l2.append({'pattern': ng_str, 'count': row[1]})

    pcon.close()

    # 危険スコア計算
    # Layer1マッチ = 高危険(0.6), Layer2マッチ = 中危険(0.3)
    total_ngrams = len(ngrams)
    l1_score = min(len(matched_l1) / total_ngrams * 0.6, 0.6) if total_ngrams > 0 else 0
    l2_score = min(len(matched_l2) / total_ngrams * 0.3, 0.3) if total_ngrams > 0 else 0
    danger_score = round(min(l1_score + l2_score, 1.0), 3)

    if danger_score >= threshold:
        if danger_score >= 0.6:
            prediction = 'CRITICAL'
        elif danger_score >= 0.4:
            prediction = 'DANGER'
        else:
            prediction = 'WARNING'
    else:
        prediction = 'SAFE'

    # 予測結果をDBに記録
    now = datetime.datetime.now().isoformat()
    pcon = sqlite3.connect(PATTERN_DB)
    pcur = pcon.cursor()
    pcur.execute('''INSERT INTO predictions(text, tokens, danger_score, matched_patterns, prediction, created_at)
                   VALUES(?,?,?,?,?,?)''',
                (text[:200],
                 json.dumps([t['surface'] for t in tokens], ensure_ascii=False),
                 danger_score,
                 json.dumps({'l1': matched_l1[:5], 'l2': matched_l2[:5]}, ensure_ascii=False),
                 prediction, now))
    pcon.commit()
    pcon.close()

    return {
        'text': text[:80],
        'tokens': [t['surface'] for t in tokens],
        'danger_score': danger_score,
        'matched_l1': matched_l1[:5],
        'matched_l2': matched_l2[:5],
        'prediction': prediction,
        'interpretation': f'失敗経路への進入確率: {danger_score*100:.1f}%'
    }

if __name__ == '__main__':
    print('='*50)
    print('MoCKA Morphology Engine v1.0')
    print('='*50)

    # 1. DB初期化
    init_pattern_db()

    # 2. 失敗パターンライブラリ構築
    print('\n失敗パターンライブラリ構築中...')
    build_pattern_library()

    # 3. パターン数確認
    pcon = sqlite3.connect(PATTERN_DB)
    pcur = pcon.cursor()
    pcur.execute('SELECT layer, COUNT(*), SUM(count) FROM patterns GROUP BY layer')
    for row in pcur.fetchall():
        label = 'Layer1(重大)' if row[0]==1 else 'Layer2(軽微)'
        print(f'{label}: ユニークパターン{row[1]}件 / 総出現{row[2]}回')
    pcon.close()

    # 4. テスト予測
    print('\n=== 予測テスト ===')
    test_cases = [
        'またpython直接実行を指示された',
        'ファイルを分割して渡してください',
        'エラーが発生しました、また同じ問題です',
        'mocka_senderの稼働確認完了',
        'こんにちは、今日もよろしく',
    ]

    for text in test_cases:
        result = predict(text)
        print(f'\n入力: {result["text"]}')
        print(f'  tokens: {result["tokens"]}')
        print(f'  危険スコア: {result["danger_score"]} -> {result["prediction"]}')
        if result['matched_l1']:
            print(f'  Layer1マッチ: {[m["pattern"] for m in result["matched_l1"]]}')
        if result['matched_l2']:
            print(f'  Layer2マッチ: {[m["pattern"] for m in result["matched_l2"]]}')

    print('\n' + '='*50)
    print('morphology_patterns.db 構築完了')
    print('使用方法: from morphology_engine import predict')
    print('result = predict("テキスト")')
    print('='*50)
