import csv, os, json, hashlib
from collections import defaultdict
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

def calc_rr(results):
    covered = sum(1 for s in results.values() if s['found'])
    return round(covered/len(results)*100, 1)

def calc_wrr(results):
    score = sum(s['weight'] for s in results.values() if s['found'])
    return round(score/TOTAL_WEIGHT*100, 1)

# 日付別にテキストを収集
dates = defaultdict(str)
with open(r'C:\Users\sirok\MoCKA\data\events.csv', 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        parts = line.split(',')
        if len(parts) > 1 and len(parts[1]) >= 10 and parts[1][:4] == '2026':
            date = parts[1][:10]
            dates[date] += line + ' '

target_dates = ['2026-03-26','2026-03-29','2026-03-31','2026-04-01','2026-04-02','2026-04-03','2026-04-04']

print('')
print('=' * 60)
print('  MoCKA あり: 日付別 Recovery Rate')
print('=' * 60)
print('  日付         件数    Basic RR  Weighted RR  欠損ステージ')
print('  ' + '-'*55)

os.makedirs('results', exist_ok=True)
summary = []

for date in target_dates:
    if date not in dates:
        continue
    text = dates[date]
    results = analyze(text)
    rr = calc_rr(results)
    wrr = calc_wrr(results)
    missing = [s for s,v in results.items() if not v['found']]
    line_count = text.count('2026')
    print('  {} {:>4}件   {:>6}%   {:>6}%   {}'.format(
        date, line_count, rr, wrr, ','.join(missing) if missing else 'なし'))
    summary.append({'date':date,'basic_rr':rr,'weighted_rr':wrr,'missing':missing})

avg_rr = round(sum(s['basic_rr'] for s in summary)/len(summary), 1)
avg_wrr = round(sum(s['weighted_rr'] for s in summary)/len(summary), 1)
print('  ' + '-'*55)
print('  平均         Basic RR: {}%   Weighted RR: {}%'.format(avg_rr, avg_wrr))
print('=' * 60)

with open('results/A1_by_date_' + datetime.now().strftime('%Y%m%d') + '.json', 'w', encoding='utf-8') as f:
    json.dump({'experiment':'A1_by_date','summary':summary,'avg_basic_rr':avg_rr,'avg_weighted_rr':avg_wrr}, f, ensure_ascii=False, indent=2)
print('  Saved: results/A1_by_date.json')
