# -*- coding: utf-8 -*-
"""
MoCKA Morphology Engine v1.0
蠖｢諷狗ｴ隗｣譫・+ 邨・∩蜷医ｏ縺帛・迴ｾ遒ｺ邇・お繝ｳ繧ｸ繝ｳ
AYX+TS逅・ｫ門ｮ溯｣・ 繧ｴ繝ｼ繝ｫ縺ｯ蝗ｺ螳夂せ縺ｧ縺ｯ縺ｪ縺城｣邯夐ｲ陦後☆繧句､牙喧霆ｸ縺ｮ荳ｭ縺ｫ縺ゅｋ

蜃ｦ逅・ヵ繝ｭ繝ｼ:
1. 繝・く繧ｹ繝医ｒ蠖｢諷狗ｴ隗｣譫・Janome)縺ｧ蛻・ｧ｣
2. 蜩∬ｩ槭ヵ繧｣繝ｫ繧ｿ繝ｪ繝ｳ繧ｰ(荳ｻ隱・霑ｰ隱・蜍戊ｩ・蠖｢螳ｹ隧・蜷崎ｩ・
3. N-gram邨・∩蜷医ｏ縺帷函謌・4. 驕主悉縺ｮ螟ｱ謨嶺ｺ倶ｾ・Layer1/Layer2)縺ｨ縺ｮ辣ｧ蜷・5. 蜃ｺ迴ｾ遒ｺ邇・ｒ邂怜・ -> 髢ｾ蛟､雜・〒DANGER隴ｦ蜻・"""
import json, sqlite3, sys, datetime, itertools
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

BASE    = Path(r'C:\Users\sirok\MoCKA')
DB_PATH = BASE / 'data' / 'mocka_events.db'
PATTERN_DB = BASE / 'data' / 'morphology_patterns.db'
HEINRICH = BASE / 'data' / 'heinrich_report.json'

# ===== 蜩∬ｩ槭ヵ繧｣繝ｫ繧ｿ =====
# 諢丞袖繧呈戟縺､蜩∬ｩ槭・縺ｿ謚ｽ蜃ｺ(蜉ｩ隧槭・蜉ｩ蜍戊ｩ槭・險伜捷繧帝勁螟・
VALID_POS = {
    '蜷崎ｩ・, '蜍戊ｩ・, '蠖｢螳ｹ隧・, '蜑ｯ隧・, '諢溷虚隧・
}
INVALID_SURFACE = {
    '繧・, '縺ｯ', '縺・, '縺ｫ', '縺ｧ', '縺ｨ', '繧・, '縺ｮ', '縺ｸ',
    '縺九ｉ', '縺ｾ縺ｧ', '繧医ｊ', '縺ｪ縺ｩ', '縺ｭ', '繧・, '縺・, '繧・, '縺・,
    '縺ｦ', '縺・, '縺・, '縺ｪ', '縺', '縺ｧ縺・, '縺ｾ縺・, '縺ｪ縺・
}

def tokenize(text):
    """Janome縺ｧ蠖｢諷狗ｴ隗｣譫・-> 諢丞袖縺ｮ縺ゅｋ蜩∬ｩ槭・縺ｿ霑斐☆"""
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
    """N-gram邨・∩蜷医ｏ縺帷函謌・2-gram + 3-gram)"""
    surfaces = [t['surface'] for t in tokens]
    ngrams = []
    for size in range(2, n+2):
        for i in range(len(surfaces) - size + 1):
            ngrams.append(tuple(surfaces[i:i+size]))
    return ngrams

def init_pattern_db():
    """繝代ち繝ｼ繝ｳDB繧貞・譛溷喧"""
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
    print('morphology_patterns.db 蛻晄悄蛹門ｮ御ｺ・)

def build_pattern_library():
    """
    events.db縺ｮLayer1/Layer2繧､繝吶Φ繝医°繧・    螟ｱ謨励ヱ繧ｿ繝ｼ繝ｳ縺ｮN-gram霎樊嶌繧呈ｧ狗ｯ・    """
    # 繝上う繝ｳ繝ｪ繝・ヲ繝ｬ繝昴・繝医°繧・Layer1/Layer2繧ｵ繝ｳ繝励Ν蜿門ｾ・    heinrich = json.load(open(HEINRICH, encoding='utf-8'))
    layer1_ids = {s['event_id'] for s in heinrich['heinrich']['layer1_critical'].get('samples', []) 
                  if isinstance(heinrich['heinrich']['layer1_critical'], dict) and 'samples' in heinrich['heinrich']['layer1_critical']}

    # events.db縺九ｉ蜈ｨLayer1/Layer2繝・く繧ｹ繝医ｒ蜿門ｾ・    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # Layer1: 驥榊､ｧ莠区腐
    layer1_types = ('MATAKA', 'CLAIM', 'INTEGRITY_VIOLATION', 'CRITICAL', 'INSTRUCTION_IGNORE')
    placeholders = ','.join('?' * len(layer1_types))
    cur.execute(f"SELECT event_id, what_type, title, why_purpose FROM events WHERE what_type IN ({placeholders})", layer1_types)
    layer1_rows = cur.fetchall()

    # Layer2: 霆ｽ蠕ｮ縺ｪ莠区腐
    layer2_keywords = ['error', 'fail', 'timeout', 'exception']
    cur.execute("SELECT event_id, what_type, title, why_purpose FROM events WHERE what_type IN ('DANGER','ERROR','INCIDENT','recurrence')")
    layer2_rows = cur.fetchall()
    con.close()

    # 繝代ち繝ｼ繝ｳDB讒狗ｯ・    pcon = sqlite3.connect(PATTERN_DB)
    pcur = pcon.cursor()
    now = datetime.datetime.now().isoformat()

    # cache: skip processed event_ids
    pcur.execute("SELECT DISTINCT event_id FROM patterns WHERE event_id IS NOT NULL")
    cached_ids = {r[0] for r in pcur.fetchall()}
    print(f"cache hit: {len(cached_ids)} skipped")
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
    print(f'Layer1繝代ち繝ｼ繝ｳ逋ｻ骭ｲ: {l1_patterns}莉ｶ')
    print(f'Layer2繝代ち繝ｼ繝ｳ逋ｻ骭ｲ: {l2_patterns}莉ｶ')

def predict(text, threshold=0.3):
    """
    蜈･蜉帙ユ繧ｭ繧ｹ繝医ｒ隗｣譫舌＠縺ｦ螟ｱ謨礼ｵ瑚ｷｯ縺ｸ縺ｮ騾ｲ蜈･遒ｺ邇・ｒ霑斐☆
    threshold: 0.0-1.0 (縺薙・蛟､繧定ｶ・∴繧九→DANGER)
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
        # Layer1繝槭ャ繝・驥榊､ｧ莠区腐繝代ち繝ｼ繝ｳ)
        pcur.execute('SELECT ngram, count FROM patterns WHERE ngram=? AND layer=1', (ng_str,))
        row = pcur.fetchone()
        if row:
            matched_l1.append({'pattern': ng_str, 'count': row[1]})
        # Layer2繝槭ャ繝・霆ｽ蠕ｮ莠区腐繝代ち繝ｼ繝ｳ)
        pcur.execute('SELECT ngram, count FROM patterns WHERE ngram=? AND layer=2', (ng_str,))
        row = pcur.fetchone()
        if row:
            matched_l2.append({'pattern': ng_str, 'count': row[1]})

    pcon.close()

    # 蜊ｱ髯ｺ繧ｹ繧ｳ繧｢險育ｮ・    # Layer1繝槭ャ繝・= 鬮伜些髯ｺ(0.6), Layer2繝槭ャ繝・= 荳ｭ蜊ｱ髯ｺ(0.3)
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

    # 莠域ｸｬ邨先棡繧奪B縺ｫ險倬鹸
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
        'interpretation': f'螟ｱ謨礼ｵ瑚ｷｯ縺ｸ縺ｮ騾ｲ蜈･遒ｺ邇・ {danger_score*100:.1f}%'
    }

if __name__ == '__main__':
    print('='*50)
    print('MoCKA Morphology Engine v1.0')
    print('='*50)

    # 1. DB蛻晄悄蛹・    init_pattern_db()

    # 2. 螟ｱ謨励ヱ繧ｿ繝ｼ繝ｳ繝ｩ繧､繝悶Λ繝ｪ讒狗ｯ・    print('\n螟ｱ謨励ヱ繧ｿ繝ｼ繝ｳ繝ｩ繧､繝悶Λ繝ｪ讒狗ｯ我ｸｭ...')
    build_pattern_library()

    # 3. 繝代ち繝ｼ繝ｳ謨ｰ遒ｺ隱・    pcon = sqlite3.connect(PATTERN_DB)
    pcur = pcon.cursor()
    pcur.execute('SELECT layer, COUNT(*), SUM(count) FROM patterns GROUP BY layer')
    for row in pcur.fetchall():
        label = 'Layer1(驥榊､ｧ)' if row[0]==1 else 'Layer2(霆ｽ蠕ｮ)'
        print(f'{label}: 繝ｦ繝九・繧ｯ繝代ち繝ｼ繝ｳ{row[1]}莉ｶ / 邱丞・迴ｾ{row[2]}蝗・)
    pcon.close()

    # 4. 繝・せ繝井ｺ域ｸｬ
    print('\n=== 莠域ｸｬ繝・せ繝・===')
    test_cases = [
        '縺ｾ縺殫ython逶ｴ謗･螳溯｡後ｒ謖・､ｺ縺輔ｌ縺・,
        '繝輔ぃ繧､繝ｫ繧貞・蜑ｲ縺励※貂｡縺励※縺上□縺輔＞',
        '繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆縲√∪縺溷酔縺伜撫鬘後〒縺・,
        'mocka_sender縺ｮ遞ｼ蜒咲｢ｺ隱榊ｮ御ｺ・,
        '縺薙ｓ縺ｫ縺｡縺ｯ縲∽ｻ頑律繧ゅｈ繧阪＠縺・,
    ]

    for text in test_cases:
        result = predict(text)
        print(f'\n蜈･蜉・ {result["text"]}')
        print(f'  tokens: {result["tokens"]}')
        print(f'  蜊ｱ髯ｺ繧ｹ繧ｳ繧｢: {result["danger_score"]} -> {result["prediction"]}')
        if result['matched_l1']:
            print(f'  Layer1繝槭ャ繝・ {[m["pattern"] for m in result["matched_l1"]]}')
        if result['matched_l2']:
            print(f'  Layer2繝槭ャ繝・ {[m["pattern"] for m in result["matched_l2"]]}')

    print('\n' + '='*50)
    print('morphology_patterns.db 讒狗ｯ牙ｮ御ｺ・)
    print('菴ｿ逕ｨ譁ｹ豕・ from morphology_engine import predict')
    print('result = predict("繝・く繧ｹ繝・)')
    print('='*50)
