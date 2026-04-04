import json, os, hashlib
from datetime import datetime

STAGES = {
    'Observation': {'keywords': ['\u89b3\u5bdf','observation','\u78ba\u8a8d','\u767a\u898b','observe','\u691c\u77e5'], 'weight': 1.0},
    'Record':      {'keywords': ['\u8a18\u9332','record','log','\u4fdd\u5b58','save','\u767b\u9332'], 'weight': 1.0},
    'Incident':    {'keywords': ['\u30a4\u30f3\u30b7\u30c7\u30f3\u30c8','incident','\u30a8\u30e9\u30fc','\u554f\u984c','error','failure'], 'weight': 2.0},
    'Recurrence':  {'keywords': ['\u518d\u767a','recurrence','\u7e70\u308a\u8fd4\u3057','repeat','\u53cd\u5fa9'], 'weight': 1.0},
    'Prevention':  {'keywords': ['\u9632\u6b62','prevention','\u5bfe\u7b56','prevent','\u6539\u5584','\u56de\u907f'], 'weight': 2.0},
    'Decision':    {'keywords': ['\u6c7a\u5b9a','decision','\u5224\u65ad','decide','\u9078\u629e','\u63a1\u7528'], 'weight': 1.5},
    'Action':      {'keywords': ['\u5b9f\u884c','action','\u64cd\u4f5c','execute','\u5b9f\u65bd','run'], 'weight': 1.0},
    'Audit':       {'keywords': ['\u76e3\u67fb','audit','\u691c\u8a3c','verify','\u78ba\u8a8d\u6e08','validate'], 'weight': 1.5},
}
TOTAL_WEIGHT = sum(s['weight'] for s in STAGES.values())

RE_REDUCED_DIR = r'C:\Users\sirok\MoCKA\data\storage\infield\RE_REDUCED'
CORE_DIR = r'C:\Users\sirok\MoCKA\data\storage\infield\CORE'

os.makedirs(CORE_DIR, exist_ok=True)

def analyze(text):
    t = text.lower()
    results = {}
    for stage, cfg in STAGES.items():
        count = sum(t.count(k.lower()) for k in cfg['keywords'])
        results[stage] = {'found': count>0, 'count': count, 'weight': cfg['weight']}
    return results

def calc_wrr(results):
    score = sum(s['weight'] for s in results.values() if s['found'])
    return round(score/TOTAL_WEIGHT*100, 1)

print('')
print('=' * 60)
print('  CORE生成: RE_REDUCED → 8ステージ分類')
print('=' * 60)

processed = 0
for fname in sorted(os.listdir(RE_REDUCED_DIR)):
    if not fname.endswith('.json'):
        continue

    # 既にCORE済みならスキップ
    core_fname = fname.replace('EN8N','CORE').replace('ERRD','CORE')
    core_path = os.path.join(CORE_DIR, core_fname)
    if os.path.exists(core_path):
        print('  SKIP: ' + fname[:40])
        continue

    src_path = os.path.join(RE_REDUCED_DIR, fname)
    with open(src_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # extractionテキストを取得
    text = data.get('extraction', '')
    if not text:
        print('  SKIP(no extraction): ' + fname[:40])
        continue

    # 8ステージ分類
    results = analyze(text)
    wrr = calc_wrr(results)
    missing = [s for s,v in results.items() if not v['found']]
    covered = [s for s,v in results.items() if v['found']]

    # COREデータ作成
    core_data = {
        'event_id': fname.replace('.json','').replace('EN8N','CORE').replace('ERRD','CORE'),
        'source_re_reduced': fname,
        'source': data.get('source',''),
        'origin_file': data.get('origin_file',''),
        'timestamp': datetime.now().isoformat(),
        'stage_classification': {
            stage: {
                'found': v['found'],
                'count': v['count'],
                'weight': v['weight']
            } for stage, v in results.items()
        },
        'covered_stages': covered,
        'missing_stages': missing,
        'core_rr': wrr,
        'source_restore_rate': data.get('restore_rate', 0),
        'hash': hashlib.sha256(text.encode('utf-8', errors='ignore')).hexdigest()[:16],
        'pipeline': 'mocka_core_v1_local'
    }

    with open(core_path, 'w', encoding='utf-8') as f:
        json.dump(core_data, f, ensure_ascii=False, indent=2)

    print('  [{:>2}] {:>5}% | covered: {} | {}'.format(
        processed+1, wrr, len(covered), fname[:35]))
    processed += 1

print('=' * 60)
print('  CORE生成完了: {}件'.format(processed))
print('  保存先: ' + CORE_DIR)
