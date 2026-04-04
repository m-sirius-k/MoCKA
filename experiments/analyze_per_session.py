import json, os
from datetime import datetime

STAGES = {
    'Observation': {'keywords': ['\u89b3\u5bdf','observation','\u78ba\u8a8d','\u767a\u898b'], 'weight': 1.0},
    'Record':      {'keywords': ['\u8a18\u9332','record','log','\u4fdd\u5b58'], 'weight': 1.0},
    'Incident':    {'keywords': ['\u30a4\u30f3\u30b7\u30c7\u30f3\u30c8','incident','\u30a8\u30e9\u30fc','\u554f\u984c'], 'weight': 2.0},
    'Recurrence':  {'keywords': ['\u518d\u767a','recurrence','\u7e70\u308a\u8fd4\u3057'], 'weight': 1.0},
    'Prevention':  {'keywords': ['\u9632\u6b62','prevention','\u5bfe\u7b56','\u6539\u5584'], 'weight': 2.0},
    'Decision':    {'keywords': ['\u6c7a\u5b9a','decision','\u5224\u65ad'], 'weight': 1.5},
    'Action':      {'keywords': ['\u5b9f\u884c','action','\u64cd\u4f5c'], 'weight': 1.0},
    'Audit':       {'keywords': ['\u76e3\u67fb','audit','\u691c\u8a3c'], 'weight': 1.5},
}
TOTAL_WEIGHT = sum(s['weight'] for s in STAGES.values())

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

# RAWフォルダの各ファイル = 各チャットセッション
raw_dir = r'C:\Users\sirok\MoCKA\data\storage\infield\RAW'
files = [f for f in os.listdir(raw_dir) if f.endswith('.json')]

print('')
print('=' * 65)
print('  MoCKA評価: 1チャットセッション = 1試験単位')
print('=' * 65)
print('  ファイル                          サイズ   Weighted RR  欠損')
print('  ' + '-'*60)

results_all = []
for fname in sorted(files):
    path = os.path.join(raw_dir, fname)
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    if len(text) < 100:
        continue
    r = analyze(text)
    wrr = calc_wrr(r)
    missing = [s for s,v in r.items() if not v['found']]
    source = 'COPI' if 'COPI' in fname else 'CLAU' if 'CLAU' in fname else 'GEMI' if 'GEMI' in fname else 'CHAT'
    print('  {:<35} {:>6}字  {:>6}%   {}'.format(
        fname[:35], len(text), wrr, len(missing)))
    results_all.append({'file':fname,'source':source,'size':len(text),'wrr':wrr,'missing':missing})

avg = round(sum(r['wrr'] for r in results_all)/len(results_all), 1) if results_all else 0
print('  ' + '-'*60)
print('  平均 Weighted RR: {}%  ({} セッション)'.format(avg, len(results_all)))
print('=' * 65)

with open('results/A1_per_session_' + datetime.now().strftime('%Y%m%d') + '.json', 'w', encoding='utf-8') as f:
    json.dump({'experiment':'A1_per_session','sessions':results_all,'avg_wrr':avg}, f, ensure_ascii=False, indent=2)
print('  Saved.')
