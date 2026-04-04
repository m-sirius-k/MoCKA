import json, os, hashlib
from datetime import datetime

# Recurrenceを強化したSTAGES定義
STAGES = {
    'Observation': {'keywords': ['\u89b3\u5bdf','observation','\u78ba\u8a8d','\u767a\u898b','observe','\u691c\u77e5','\u8a8d\u8b58','\u6ce8\u76ee'], 'weight': 1.0},
    'Record':      {'keywords': ['\u8a18\u9332','record','log','\u4fdd\u5b58','save','\u767b\u9332','\u8a18\u8f09','\u4fdd\u7ba1','\u5c65\u6b74'], 'weight': 1.0},
    'Incident':    {'keywords': ['\u30a4\u30f3\u30b7\u30c7\u30f3\u30c8','incident','\u30a8\u30e9\u30fc','\u554f\u984c','error','failure','\u969c\u5bb3','\u4e0d\u5177\u5408','\u5931\u6557','\u30d0\u30b0'], 'weight': 2.0},
    'Recurrence':  {'keywords': [
        '\u518d\u767a','recurrence','\u7e70\u308a\u8fd4\u3057','repeat','\u53cd\u5fa9',
        '\u518d\u5ea6','\u518d\u73fe','\u540c\u69d8','\u540c\u3058\u554f\u984c',
        '\u518d\u8a66','\u5fa9\u6d3b','\u7d99\u7d9a','\u6539\u5584',
        'again','loop','\u30eb\u30fc\u30d7','\u30d1\u30bf\u30fc\u30f3',
        '\u8ab2\u984c','\u69cb\u9020\u7684','\u6301\u7d9a','\u7dad\u6301'
    ], 'weight': 1.0},
    'Prevention':  {'keywords': ['\u9632\u6b62','prevention','\u5bfe\u7b56','prevent','\u6539\u5584','\u56de\u907f','\u5bfe\u5fdc','\u89e3\u6c7a','\u6539\u5584\u7b56','\u5bfe\u51e6'], 'weight': 2.0},
    'Decision':    {'keywords': ['\u6c7a\u5b9a','decision','\u5224\u65ad','decide','\u9078\u629e','\u63a1\u7528','\u65b9\u9488','\u5c55\u958b','\u8a2d\u8a08','\u8a2d\u5b9a'], 'weight': 1.5},
    'Action':      {'keywords': ['\u5b9f\u884c','action','\u64cd\u4f5c','execute','\u5b9f\u65bd','run','\u69cb\u7bc9','\u5c0e\u5165','\u9069\u7528','\u5b9f\u88c5'], 'weight': 1.0},
    'Audit':       {'keywords': ['\u76e3\u67fb','audit','\u691c\u8a3c','verify','\u78ba\u8a8d\u6e08','validate','\u8a55\u4fa1','\u691c\u8a0e','\u5206\u6790','\u8a3c\u660e'], 'weight': 1.5},
}
TOTAL_WEIGHT = sum(s['weight'] for s in STAGES.values())

CORE_DIR    = r'C:\Users\sirok\MoCKA\data\storage\infield\CORE'
RE_DIR      = r'C:\Users\sirok\MoCKA\data\storage\infield\RE_REDUCED'
ESSENCE_DIR = r'C:\Users\sirok\MoCKA\data\storage\infield\ESSENCE'
OUTBOX_DIR  = r'C:\Users\sirok\MoCKA\data\storage\outbox\RAW'

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
print('  CORE v2生成: Recurrence強化版')
print('=' * 60)

processed = 0
for fname in sorted(os.listdir(RE_DIR)):
    if not fname.endswith('.json'):
        continue

    with open(os.path.join(RE_DIR, fname), 'r', encoding='utf-8') as f:
        data = json.load(f)

    text = data.get('extraction', '')
    if not text:
        print('  SKIP(no extraction): ' + fname[:40])
        continue

    results = analyze(text)
    wrr = calc_wrr(results)
    covered = [s for s,v in results.items() if v['found']]
    missing = [s for s,v in results.items() if not v['found']]
    rec = results.get('Recurrence', {})

    core_fname = fname.replace('EN8N','CORE').replace('ERRD','CORE')
    core_path = os.path.join(CORE_DIR, core_fname)

    core_data = {
        'event_id': core_fname.replace('.json',''),
        'source_re_reduced': fname,
        'source': data.get('source',''),
        'timestamp': datetime.now().isoformat(),
        'stage_classification': {
            stage: {'found': v['found'], 'count': v['count'], 'weight': v['weight']}
            for stage, v in results.items()
        },
        'covered_stages': covered,
        'missing_stages': missing,
        'core_rr': wrr,
        'source_restore_rate': data.get('restore_rate', 0),
        'hash': hashlib.sha256(text.encode('utf-8', errors='ignore')).hexdigest()[:16],
        'pipeline': 'mocka_core_v2_recurrence_enhanced'
    }

    with open(core_path, 'w', encoding='utf-8') as f:
        json.dump(core_data, f, ensure_ascii=False, indent=2)

    rec_mark = "Rec:OK" if rec.get('found') else "Rec:--"
    print('  [{:>2}] {:>5}% {} | covered:{} | {}'.format(
        processed+1, wrr, rec_mark, len(covered), fname[:30]))
    processed += 1

print('=' * 60)
print('  CORE v2生成完了: {}件'.format(processed))

# ESSENCE v2も自動生成
from collections import defaultdict
cores = []
stage_totals = defaultdict(lambda: {'found':0,'total':0,'count_sum':0})

for fname in sorted(os.listdir(CORE_DIR)):
    if not fname.endswith('.json'):
        continue
    with open(os.path.join(CORE_DIR, fname), 'r', encoding='utf-8') as f:
        c = json.load(f)
    cores.append(c)
    for stage, v in c.get('stage_classification', {}).items():
        stage_totals[stage]['total'] += 1
        if v['found']:
            stage_totals[stage]['found'] += 1
        stage_totals[stage]['count_sum'] += v['count']

avg_rr = round(sum(c.get('core_rr',0) for c in cores)/len(cores), 1) if cores else 0
stage_summary = {}
for stage, v in stage_totals.items():
    coverage = round(v['found']/v['total']*100, 1) if v['total'] else 0
    stage_summary[stage] = {'coverage_pct': coverage, 'found_in': v['found'], 'total_cores': v['total']}

strongest = max(stage_summary.items(), key=lambda x: x[1]['coverage_pct'])
weakest   = min(stage_summary.items(), key=lambda x: x[1]['coverage_pct'])

ts = datetime.now().strftime('%Y%m%d_%H%M%S')
essence = {
    'event_id': 'ESSENCE_v2_' + ts,
    'timestamp': datetime.now().isoformat(),
    'pipeline': 'mocka_essence_v2',
    'summary': {
        'total_cores': len(cores),
        'avg_core_rr': avg_rr,
        'strongest_stage': {'stage': strongest[0], 'coverage': strongest[1]['coverage_pct']},
        'weakest_stage':   {'stage': weakest[0],   'coverage': weakest[1]['coverage_pct']},
    },
    'stage_coverage': stage_summary,
}

essence_path = os.path.join(ESSENCE_DIR, 'ESSENCE_v2_' + ts + '.json')
with open(essence_path, 'w', encoding='utf-8') as f:
    json.dump(essence, f, ensure_ascii=False, indent=2)

print('')
print('  ESSENCE v2 ステージカバレッジ:')
for stage, v in sorted(stage_summary.items(), key=lambda x: -x[1]['coverage_pct']):
    bar = '#' * int(v['coverage_pct']/10)
    print('  {:<12} {:>5}%  {}'.format(stage, v['coverage_pct'], bar))
print('  平均CORE RR: {}%'.format(avg_rr))
print('  ESSENCE保存: ' + essence_path)
