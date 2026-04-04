import os, hashlib
from datetime import datetime

STAGES = {
    'Observation': {'keywords': ['\u89b3\u5bdf','observation','\u78ba\u8a8d','\u767a\u898b','\u8a8d\u8b58','\u691c\u77e5'], 'weight': 1.0},
    'Record':      {'keywords': ['\u8a18\u9332','record','log','\u4fdd\u5b58','\u767b\u9332','\u5c65\u6b74'], 'weight': 1.0},
    'Incident':    {'keywords': ['\u30a4\u30f3\u30b7\u30c7\u30f3\u30c8','incident','\u30a8\u30e9\u30fc','\u554f\u984c','error','failure','\u969c\u5bb3','\u4e0d\u5177\u5408'], 'weight': 2.0},
    'Recurrence':  {'keywords': ['\u518d\u767a','recurrence','\u7e70\u308a\u8fd4\u3057','repeat','self_doubt','stop due to','again','\u518d\u73fe','\u540c\u69d8'], 'weight': 1.0},
    'Prevention':  {'keywords': ['\u9632\u6b62','prevention','\u5bfe\u7b56','prevent','\u6539\u5584','\u56de\u907f'], 'weight': 2.0},
    'Decision':    {'keywords': ['\u6c7a\u5b9a','decision','\u5224\u65ad','decide','\u9078\u629e'], 'weight': 1.5},
    'Action':      {'keywords': ['\u5b9f\u884c','action','\u64cd\u4f5c','execute','fix','applied'], 'weight': 1.0},
    'Audit':       {'keywords': ['\u76e3\u67fb','audit','\u691c\u8a3c','verify','governance','hash'], 'weight': 1.5},
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

targets = [
    (r'C:\Users\sirok\MoCKA\runtime\master_index.csv', 'master_index'),
    (r'C:\Users\sirok\MoCKA\runtime\incident_log.csv', 'incident_log'),
    (r'C:\Users\sirok\MoCKA\data\failure_log.csv', 'failure_log'),
    (r'C:\Users\sirok\MoCKA\archive\ledger_old\record\event_log.csv', 'ledger_event_log'),
    (r'C:\Users\sirok\MoCKA\mocka-governance-kernel\governance\change_log.csv', 'change_log'),
    (r'C:\Users\sirok\MoCKA\mocka-governance-kernel\governance\impact_registry.csv', 'impact_registry'),
    (r'C:\Users\sirok\MoCKA\data\events_backup_20260401_132453.csv', 'events_backup'),
    (r'C:\Users\sirok\MoCKA\data\events_legacy_backup.csv', 'events_legacy'),
]

print('')
print('=' * 65)
print('  MoCKA内部CSV: RR測定')
print('=' * 65)
print('  ファイル                  行数      WRR   欠損ステージ')
print('  ' + '-'*60)

results_all = []
for path, label in targets:
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
        lines = text.count('\n')
    r = analyze(text)
    wrr = calc_wrr(r)
    missing = [s for s,v in r.items() if not v['found']]
    print('  {:<25} {:>5}行  {:>5}%  {}'.format(
        label[:25], lines, wrr, ','.join(missing) if missing else 'なし'))
    results_all.append({'file':label,'lines':lines,'wrr':wrr,'missing':missing})

print('=' * 65)
