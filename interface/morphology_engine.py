# -*- coding: utf-8 -*-
"""
MoCKA Morphology Engine v1.0
陟厄ｽ｢隲ｷ迢暦ｽｴ・ｰ髫暦ｽ｣隴ｫ繝ｻ+ 驍ｨ繝ｻ竏ｩ陷ｷ蛹ｻ・冗ｸｺ蟶帙・霑ｴ・ｾ驕抵ｽｺ驍・・縺顔ｹ晢ｽｳ郢ｧ・ｸ郢晢ｽｳ
AYX+TS騾・・・ｫ髢・ｮ貅ｯ・｣繝ｻ 郢ｧ・ｴ郢晢ｽｼ郢晢ｽｫ邵ｺ・ｯ陜暦ｽｺ陞ｳ螟ゅ○邵ｺ・ｧ邵ｺ・ｯ邵ｺ・ｪ邵ｺ蝓篠・｣驍ｯ螟青・ｲ髯ｦ蠕娯・郢ｧ蜿･・､迚吝密髴・ｽｸ邵ｺ・ｮ闕ｳ・ｭ邵ｺ・ｫ邵ｺ繧・ｽ・

陷・ｽｦ騾・・繝ｵ郢晢ｽｭ郢晢ｽｼ:
1. 郢昴・縺冗ｹｧ・ｹ郢晏現・定厄ｽ｢隲ｷ迢暦ｽｴ・ｰ髫暦ｽ｣隴ｫ繝ｻJanome)邵ｺ・ｧ陋ｻ繝ｻ・ｧ・｣
2. 陷ｩ竏ｬ・ｩ讒ｭ繝ｵ郢ｧ・｣郢晢ｽｫ郢ｧ・ｿ郢晢ｽｪ郢晢ｽｳ郢ｧ・ｰ(闕ｳ・ｻ髫ｱ繝ｻ髴托ｽｰ髫ｱ繝ｻ陷肴・・ｩ繝ｻ陟厄ｽ｢陞ｳ・ｹ髫ｧ繝ｻ陷ｷ蟠趣ｽｩ繝ｻ
3. N-gram驍ｨ繝ｻ竏ｩ陷ｷ蛹ｻ・冗ｸｺ蟶ｷ蜃ｽ隰後・4. 鬩穂ｸｻ謔臥ｸｺ・ｮ陞滂ｽｱ隰ｨ蠍ｺ・ｺ蛟ｶ・ｾ繝ｻLayer1/Layer2)邵ｺ・ｨ邵ｺ・ｮ霎｣・ｧ陷ｷ繝ｻ5. 陷・ｽｺ霑ｴ・ｾ驕抵ｽｺ驍・・・帝ｂ諤懊・ -> 鬮｢・ｾ陋滂ｽ､髮懊・縲奪ANGER髫ｴ・ｦ陷ｻ繝ｻ"""
import json, sqlite3, sys, datetime, itertools
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

BASE    = Path(r'C:\Users\sirok\MoCKA')
DB_PATH = BASE / 'data' / 'mocka_events.db'
PATTERN_DB = BASE / 'data' / 'morphology_patterns.db'
HEINRICH = BASE / 'data' / 'heinrich_report.json'

# ===== 陷ｩ竏ｬ・ｩ讒ｭ繝ｵ郢ｧ・｣郢晢ｽｫ郢ｧ・ｿ =====
# 隲｢荳櫁｢也ｹｧ蜻域亜邵ｺ・､陷ｩ竏ｬ・ｩ讒ｭ繝ｻ邵ｺ・ｿ隰夲ｽｽ陷・ｽｺ(陷会ｽｩ髫ｧ讒ｭ繝ｻ陷会ｽｩ陷肴・・ｩ讒ｭ繝ｻ髫ｪ莨懈差郢ｧ蟶晏求陞溘・
VALID_POS = {
    '名詞', '動詞', '形容詞', '副詞', '形容動詞',
}
INVALID_SURFACE = {
    '郢ｧ繝ｻ, '邵ｺ・ｯ', '邵ｺ繝ｻ, '邵ｺ・ｫ', '邵ｺ・ｧ', '邵ｺ・ｨ', '郢ｧ繝ｻ, '邵ｺ・ｮ', '邵ｺ・ｸ',
    '邵ｺ荵晢ｽ・, '邵ｺ・ｾ邵ｺ・ｧ', '郢ｧ蛹ｻ・・, '邵ｺ・ｪ邵ｺ・ｩ', '邵ｺ・ｭ', '郢ｧ繝ｻ, '邵ｺ繝ｻ, '郢ｧ繝ｻ, '邵ｺ繝ｻ,
    '邵ｺ・ｦ', '邵ｺ繝ｻ, '邵ｺ繝ｻ, '邵ｺ・ｪ', '邵ｺ・ｰ', '邵ｺ・ｧ邵ｺ繝ｻ, '邵ｺ・ｾ邵ｺ繝ｻ, '邵ｺ・ｪ邵ｺ繝ｻ
}

def tokenize(text):
    """Janome邵ｺ・ｧ陟厄ｽ｢隲ｷ迢暦ｽｴ・ｰ髫暦ｽ｣隴ｫ繝ｻ-> 隲｢荳櫁｢也ｸｺ・ｮ邵ｺ繧・ｽ玖惓竏ｬ・ｩ讒ｭ繝ｻ邵ｺ・ｿ髴第鱒笘・""
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
    """N-gram驍ｨ繝ｻ竏ｩ陷ｷ蛹ｻ・冗ｸｺ蟶ｷ蜃ｽ隰後・2-gram + 3-gram)"""
    surfaces = [t['surface'] for t in tokens]
    ngrams = []
    for size in range(2, n+2):
        for i in range(len(surfaces) - size + 1):
            ngrams.append(tuple(surfaces[i:i+size]))
    return ngrams

def init_pattern_db():
    """郢昜ｻ｣縺｡郢晢ｽｼ郢晢ｽｳDB郢ｧ雋槭・隴帶ｺｷ蝟ｧ"""
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
    print('morphology_patterns.db 陋ｻ譎・ｄ陋ｹ髢・ｮ蠕｡・ｺ繝ｻ)

def build_pattern_library():
    """
    events.db邵ｺ・ｮLayer1/Layer2郢ｧ・､郢晏生ﾎｦ郢晏現ﾂｰ郢ｧ繝ｻ    陞滂ｽｱ隰ｨ蜉ｱ繝ｱ郢ｧ・ｿ郢晢ｽｼ郢晢ｽｳ邵ｺ・ｮN-gram髴取ｨ雁ｶ檎ｹｧ蜻茨ｽｧ迢暦ｽｯ繝ｻ    """
    # 郢昜ｸ翫≧郢晢ｽｳ郢晢ｽｪ郢昴・繝ｲ郢晢ｽｬ郢晄亢繝ｻ郢晏現ﾂｰ郢ｧ繝ｻLayer1/Layer2郢ｧ・ｵ郢晢ｽｳ郢晏干ﾎ晁愾髢・ｾ繝ｻ    heinrich = json.load(open(HEINRICH, encoding='utf-8'))
    layer1_ids = {s['event_id'] for s in heinrich['heinrich']['layer1_critical'].get('samples', []) 
                  if isinstance(heinrich['heinrich']['layer1_critical'], dict) and 'samples' in heinrich['heinrich']['layer1_critical']}

    # events.db邵ｺ荵晢ｽ芽怦・ｨLayer1/Layer2郢昴・縺冗ｹｧ・ｹ郢晏現・定愾髢・ｾ繝ｻ    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # Layer1: 鬩･讎奇ｽ､・ｧ闔蛹ｺ閻・
    layer1_types = ('MATAKA', 'CLAIM', 'INTEGRITY_VIOLATION', 'CRITICAL', 'INSTRUCTION_IGNORE')
    placeholders = ','.join('?' * len(layer1_types))
    cur.execute(f"SELECT event_id, what_type, title, why_purpose FROM events WHERE what_type IN ({placeholders})", layer1_types)
    layer1_rows = cur.fetchall()

    # Layer2: 髴・ｽｽ陟包ｽｮ邵ｺ・ｪ闔蛹ｺ閻・
    layer2_keywords = ['error', 'fail', 'timeout', 'exception']
    cur.execute("SELECT event_id, what_type, title, why_purpose FROM events WHERE what_type IN ('DANGER','ERROR','INCIDENT','recurrence')")
    layer2_rows = cur.fetchall()
    con.close()

    # 郢昜ｻ｣縺｡郢晢ｽｼ郢晢ｽｳDB隶堤距・ｯ繝ｻ    pcon = sqlite3.connect(PATTERN_DB)
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
            if event_id in cached_ids: continue  # skip cached
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
    print(f'Layer1郢昜ｻ｣縺｡郢晢ｽｼ郢晢ｽｳ騾具ｽｻ鬪ｭ・ｲ: {l1_patterns}闔会ｽｶ')
    print(f'Layer2郢昜ｻ｣縺｡郢晢ｽｼ郢晢ｽｳ騾具ｽｻ鬪ｭ・ｲ: {l2_patterns}闔会ｽｶ')

def predict(text, threshold=0.3):
    """
    陷茨ｽ･陷牙ｸ吶Θ郢ｧ・ｭ郢ｧ・ｹ郢晏現・帝囓・｣隴ｫ闊鯉ｼ邵ｺ・ｦ陞滂ｽｱ隰ｨ遉ｼ・ｵ迹夲ｽｷ・ｯ邵ｺ・ｸ邵ｺ・ｮ鬨ｾ・ｲ陷茨ｽ･驕抵ｽｺ驍・・・帝恆譁絶・
    threshold: 0.0-1.0 (邵ｺ阮吶・陋滂ｽ､郢ｧ螳夲ｽｶ繝ｻ竏ｴ郢ｧ荵昶・DANGER)
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
        # Layer1郢晄ｧｭ繝｣郢昴・鬩･讎奇ｽ､・ｧ闔蛹ｺ閻千ｹ昜ｻ｣縺｡郢晢ｽｼ郢晢ｽｳ)
        pcur.execute('SELECT ngram, count FROM patterns WHERE ngram=? AND layer=1', (ng_str,))
        row = pcur.fetchone()
        if row:
            matched_l1.append({'pattern': ng_str, 'count': row[1]})
        # Layer2郢晄ｧｭ繝｣郢昴・髴・ｽｽ陟包ｽｮ闔蛹ｺ閻千ｹ昜ｻ｣縺｡郢晢ｽｼ郢晢ｽｳ)
        pcur.execute('SELECT ngram, count FROM patterns WHERE ngram=? AND layer=2', (ng_str,))
        row = pcur.fetchone()
        if row:
            matched_l2.append({'pattern': ng_str, 'count': row[1]})

    pcon.close()

    # 陷奇ｽｱ鬮ｯ・ｺ郢ｧ・ｹ郢ｧ・ｳ郢ｧ・｢髫ｪ閧ｲ・ｮ繝ｻ    # Layer1郢晄ｧｭ繝｣郢昴・= 鬯ｮ莨應ｺ幃ｫｯ・ｺ(0.6), Layer2郢晄ｧｭ繝｣郢昴・= 闕ｳ・ｭ陷奇ｽｱ鬮ｯ・ｺ(0.3)
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

    # 闔蝓滂ｽｸ・ｬ驍ｨ蜈域｣｡郢ｧ螂ｪB邵ｺ・ｫ髫ｪ蛟ｬ鮖ｸ
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
        'interpretation': f'陞滂ｽｱ隰ｨ遉ｼ・ｵ迹夲ｽｷ・ｯ邵ｺ・ｸ邵ｺ・ｮ鬨ｾ・ｲ陷茨ｽ･驕抵ｽｺ驍・・ {danger_score*100:.1f}%'
    }

if __name__ == '__main__':
    print('='*50)
    print('MoCKA Morphology Engine v1.0')
    print('='*50)

    # 1. DB陋ｻ譎・ｄ陋ｹ繝ｻ    init_pattern_db()

    # 2. 陞滂ｽｱ隰ｨ蜉ｱ繝ｱ郢ｧ・ｿ郢晢ｽｼ郢晢ｽｳ郢晢ｽｩ郢ｧ・､郢晄じﾎ帷ｹ晢ｽｪ隶堤距・ｯ繝ｻ    print('\n陞滂ｽｱ隰ｨ蜉ｱ繝ｱ郢ｧ・ｿ郢晢ｽｼ郢晢ｽｳ郢晢ｽｩ郢ｧ・､郢晄じﾎ帷ｹ晢ｽｪ隶堤距・ｯ謌托ｽｸ・ｭ...')
    build_pattern_library()

    # 3. 郢昜ｻ｣縺｡郢晢ｽｼ郢晢ｽｳ隰ｨ・ｰ驕抵ｽｺ髫ｱ繝ｻ    pcon = sqlite3.connect(PATTERN_DB)
    pcur = pcon.cursor()
    pcur.execute('SELECT layer, COUNT(*), SUM(count) FROM patterns GROUP BY layer')
    for row in pcur.fetchall():
        label = 'Layer1(鬩･讎奇ｽ､・ｧ)' if row[0]==1 else 'Layer2(髴・ｽｽ陟包ｽｮ)'
        print(f'{label}: 郢晢ｽｦ郢昜ｹ昴・郢ｧ・ｯ郢昜ｻ｣縺｡郢晢ｽｼ郢晢ｽｳ{row[1]}闔会ｽｶ / 驍ｱ荳槭・霑ｴ・ｾ{row[2]}陜励・)
    pcon.close()

    # 4. 郢昴・縺帷ｹ昜ｺ包ｽｺ蝓滂ｽｸ・ｬ
    print('\n=== 闔蝓滂ｽｸ・ｬ郢昴・縺帷ｹ昴・===')
    test_cases = [
        '邵ｺ・ｾ邵ｺ谿ｫython騾ｶ・ｴ隰暦ｽ･陞ｳ貅ｯ・｡蠕鯉ｽ定ｬ悶・・､・ｺ邵ｺ霈費ｽ檎ｸｺ繝ｻ,
        '郢晁ｼ斐＜郢ｧ・､郢晢ｽｫ郢ｧ雋槭・陷托ｽｲ邵ｺ蜉ｱ窶ｻ雋ゑｽ｡邵ｺ蜉ｱ窶ｻ邵ｺ荳岩味邵ｺ霈費ｼ・,
        '郢ｧ・ｨ郢晢ｽｩ郢晢ｽｼ邵ｺ讙主験騾墓ｺ假ｼ邵ｺ・ｾ邵ｺ蜉ｱ笳・ｸｲ竏壺穐邵ｺ貅ｷ驟皮ｸｺ莨懈牒鬯伜ｾ後堤ｸｺ繝ｻ,
        'mocka_sender邵ｺ・ｮ驕橸ｽｼ陷貞調・｢・ｺ髫ｱ讎奇ｽｮ蠕｡・ｺ繝ｻ,
        '邵ｺ阮呻ｽ鍋ｸｺ・ｫ邵ｺ・｡邵ｺ・ｯ邵ｲ竏ｽ・ｻ鬆大ｾ狗ｹｧ繧・ｽ育ｹｧ髦ｪ・邵ｺ繝ｻ,
    ]

    for text in test_cases:
        result = predict(text)
        print(f'\n陷茨ｽ･陷峨・ {result["text"]}')
        print(f'  tokens: {result["tokens"]}')
        print(f'  陷奇ｽｱ鬮ｯ・ｺ郢ｧ・ｹ郢ｧ・ｳ郢ｧ・｢: {result["danger_score"]} -> {result["prediction"]}')
        if result['matched_l1']:
            print(f'  Layer1郢晄ｧｭ繝｣郢昴・ {[m["pattern"] for m in result["matched_l1"]]}')
        if result['matched_l2']:
            print(f'  Layer2郢晄ｧｭ繝｣郢昴・ {[m["pattern"] for m in result["matched_l2"]]}')

    print('\n' + '='*50)
    print('morphology_patterns.db 隶堤距・ｯ迚呻ｽｮ蠕｡・ｺ繝ｻ)
    print('闖ｴ・ｿ騾包ｽｨ隴・ｽｹ雎輔・ from morphology_engine import predict')
    print('result = predict("郢昴・縺冗ｹｧ・ｹ郢昴・)')
    print('='*50)