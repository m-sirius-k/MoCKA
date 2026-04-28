import json, sys
sys.path.insert(0, 'interface')
from essence_classifier import add_essence

data = json.loads(open('data/success_patterns.json', encoding='utf-8').read())

count = 0
skip = 0
for key in ('hint', 'great'):
    for item in data.get(key, []):
        text = item.get('text', '')
        if '縺' in text or '繧' in text or '繝' in text:
            skip += 1
            continue
        if len(text) < 10:
            skip += 1
            continue
        result = add_essence(text, 'success_' + key)
        print(result['status'] + ' [' + key + '] ' + text[:40])
        count += 1

print('')
print('追加: ' + str(count) + '件 / スキップ(文字化け): ' + str(skip) + '件')