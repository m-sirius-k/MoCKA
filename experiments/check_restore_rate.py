import json, os

re_reduced_dir = r'C:\Users\sirok\MoCKA\data\storage\infield\RE_REDUCED'
reducing_dir = r'C:\Users\sirok\MoCKA\data\storage\infield\REDUCING'

print('')
print('=' * 60)
print('  MoCKA 固有の restore_rate 一覧')
print('=' * 60)

all_rates = []
for d in [re_reduced_dir, reducing_dir]:
    for fname in sorted(os.listdir(d)):
        if not fname.endswith('.json'):
            continue
        path = os.path.join(d, fname)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            rate = data.get('restore_rate', 'なし')
            origin = data.get('origin_file', 'なし')
            status = data.get('status', 'なし')
            print('  {} | rate={} | origin={}'.format(fname[:40], rate, origin[:30]))
            if isinstance(rate, float):
                all_rates.append(rate)
        except Exception as e:
            print('  ERR: ' + fname + ' ' + str(e))

if all_rates:
    avg = round(sum(all_rates)/len(all_rates)*100, 1)
    print('')
    print('  平均 restore_rate: {}%  ({} 件)'.format(avg, len(all_rates)))
print('=' * 60)
