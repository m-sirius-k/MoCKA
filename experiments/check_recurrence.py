import json, os

CORE_DIR = r'C:\Users\sirok\MoCKA\data\storage\infield\CORE'
RE_DIR   = r'C:\Users\sirok\MoCKA\data\storage\infield\RE_REDUCED'

print('')
print('=' * 60)
print('  Recurrence 0%の原因分析')
print('=' * 60)

for fname in sorted(os.listdir(CORE_DIR)):
    if not fname.endswith('.json'):
        continue
    with open(os.path.join(CORE_DIR, fname), 'r', encoding='utf-8') as f:
        core = json.load(f)
    
    rec = core.get('stage_classification', {}).get('Recurrence', {})
    src = core.get('source_re_reduced', '')
    
    # RE_REDUCEDのextractionを確認
    re_path = os.path.join(RE_DIR, src)
    extraction = ''
    if os.path.exists(re_path):
        with open(re_path, 'r', encoding='utf-8') as f:
            re_data = json.load(f)
        extraction = re_data.get('extraction', '')[:200]
    
    print('')
    print('  FILE: ' + fname[:40])
    print('  Recurrence found: ' + str(rec.get('found', False)))
    print('  extraction(200字): ' + extraction[:150])
