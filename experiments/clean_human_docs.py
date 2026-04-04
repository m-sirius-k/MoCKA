import json

with open('results/A0_bulk_human_docs_20260404.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 重複除去・除外処理
exclude = ['123.txt', 'MOCKA_PAPER_DRAFT', 'Microsoft Office Word']
seen = set()
valid = []

for r in data['results']:
    fname = r['file']
    # 除外チェック
    if any(e in fname for e in exclude):
        continue
    # 重複チェック
    if fname in seen:
        continue
    seen.add(fname)
    valid.append(r)

avg = round(sum(r['weighted_rr'] for r in valid)/len(valid), 1)

print('')
print('=' * 60)
print('  有効サンプル（重複除去・AI生成除外後）')
print('=' * 60)
for i, r in enumerate(valid):
    print('  A0-H{:>2} | WRR:{:>5}% | {}'.format(i+1, r['weighted_rr'], r['file'][:40]))
print('  ' + '-'*55)
print('  有効件数: {}件  平均 Weighted RR: {}%'.format(len(valid), avg))
print('=' * 60)

with open('results/A0_valid_human_docs_20260404.json', 'w', encoding='utf-8') as f:
    json.dump({'experiment':'A0_valid_human','count':len(valid),'avg_wrr':avg,'results':valid}, f, ensure_ascii=False, indent=2)
print('  Saved: results/A0_valid_human_docs_20260404.json')
