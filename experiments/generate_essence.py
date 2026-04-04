import json, os, hashlib
from datetime import datetime
from collections import defaultdict

CORE_DIR    = r'C:\Users\sirok\MoCKA\data\storage\infield\CORE'
ESSENCE_DIR = r'C:\Users\sirok\MoCKA\data\storage\infield\ESSENCE'
OUTBOX_DIR  = r'C:\Users\sirok\MoCKA\data\storage\outbox\RAW'

os.makedirs(ESSENCE_DIR, exist_ok=True)
os.makedirs(OUTBOX_DIR, exist_ok=True)

# 全COREを読み込む
cores = []
stage_totals = defaultdict(lambda: {'found':0,'total':0,'count_sum':0})

for fname in sorted(os.listdir(CORE_DIR)):
    if not fname.endswith('.json'):
        continue
    with open(os.path.join(CORE_DIR, fname), 'r', encoding='utf-8') as f:
        data = json.load(f)
    cores.append(data)
    for stage, v in data.get('stage_classification', {}).items():
        stage_totals[stage]['total'] += 1
        if v['found']:
            stage_totals[stage]['found'] += 1
        stage_totals[stage]['count_sum'] += v['count']

if not cores:
    print('COREファイルがありません')
    exit()

# ESSENCE生成
avg_rr = round(sum(c.get('core_rr',0) for c in cores)/len(cores), 1)
stage_summary = {}
for stage, v in stage_totals.items():
    coverage = round(v['found']/v['total']*100, 1) if v['total'] else 0
    stage_summary[stage] = {
        'coverage_pct': coverage,
        'found_in': v['found'],
        'total_cores': v['total'],
        'total_mentions': v['count_sum']
    }

# 最強ステージ・最弱ステージを特定
strongest = max(stage_summary.items(), key=lambda x: x[1]['coverage_pct'])
weakest   = min(stage_summary.items(), key=lambda x: x[1]['coverage_pct'])

essence = {
    'event_id': 'ESSENCE_' + datetime.now().strftime('%Y%m%d_%H%M%S'),
    'timestamp': datetime.now().isoformat(),
    'pipeline': 'mocka_essence_v1_local',
    'summary': {
        'total_cores': len(cores),
        'avg_core_rr': avg_rr,
        'strongest_stage': {'stage': strongest[0], 'coverage': strongest[1]['coverage_pct']},
        'weakest_stage':   {'stage': weakest[0],   'coverage': weakest[1]['coverage_pct']},
    },
    'stage_coverage': stage_summary,
    'core_files': [c['event_id'] for c in cores],
    'hash': hashlib.sha256(json.dumps(stage_summary).encode()).hexdigest()[:16]
}

# ESSENCE保存
ts = datetime.now().strftime('%Y%m%d_%H%M%S')
essence_path = os.path.join(ESSENCE_DIR, 'ESSENCE_' + ts + '.json')
with open(essence_path, 'w', encoding='utf-8') as f:
    json.dump(essence, f, ensure_ascii=False, indent=2)

# OUTBOX（外部共有用・簡易版）
outbox = {
    'event_id': 'OUTBOX_' + ts,
    'timestamp': datetime.now().isoformat(),
    'type': 'essence_summary',
    'avg_core_rr': avg_rr,
    'total_cores': len(cores),
    'strongest_stage': strongest[0],
    'weakest_stage': weakest[0],
    'stage_coverage': {k: v['coverage_pct'] for k,v in stage_summary.items()},
    'essence_ref': essence_path
}
outbox_path = os.path.join(OUTBOX_DIR, 'OUTBOX_' + ts + '.json')
with open(outbox_path, 'w', encoding='utf-8') as f:
    json.dump(outbox, f, ensure_ascii=False, indent=2)

# 表示
print('')
print('=' * 60)
print('  ESSENCE生成完了')
print('=' * 60)
print('  統合CORE件数  : {}件'.format(len(cores)))
print('  平均CORE RR   : {}%'.format(avg_rr))
print('  最強ステージ  : {} ({}%)'.format(strongest[0], strongest[1]['coverage_pct']))
print('  最弱ステージ  : {} ({}%)'.format(weakest[0],   weakest[1]['coverage_pct']))
print('')
print('  ステージ別カバレッジ:')
for stage, v in sorted(stage_summary.items(), key=lambda x: -x[1]['coverage_pct']):
    bar = '#' * int(v['coverage_pct']/10)
    print('  {:<12} {:>5}%  {}'.format(stage, v['coverage_pct'], bar))
print('')
print('  ESSENCE保存: ' + essence_path)
print('  OUTBOX保存 : ' + outbox_path)
print('=' * 60)
