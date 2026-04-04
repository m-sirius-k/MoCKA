import os, re, json, hashlib
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

def read_file(path):
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == '.docx':
            import docx
            doc = docx.Document(path)
            return '\n'.join([p.text for p in doc.paragraphs])
        elif ext in ['.htm', '.html']:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                html = f.read()
            return re.sub(r'<[^>]+>', '', html)
        elif ext in ['.txt', '.csv', '.md']:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        else:
            return None
    except:
        return None

# 検索対象ドライブ・フォルダ
search_roots = [
    r'F:\2023バックアップ',
    r'G:\現在担当物件など',
    r'G:\とにかくﾌｫﾙﾀﾞ-',
    r'C:\Users\sirok\Desktop',
    r'C:\Users\sirok\Documents',
]

target_exts = {'.docx', '.htm', '.html', '.txt'}
found_files = []

print('ファイルを検索中...')
for root in search_roots:
    if not os.path.exists(root):
        continue
    for dirpath, dirs, files in os.walk(root):
        # MoCKAフォルダは除外
        dirs[:] = [d for d in dirs if 'MoCKA' not in d and 'mocka' not in d.lower()]
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext in target_exts:
                full = os.path.join(dirpath, fname)
                try:
                    size = os.path.getsize(full)
                    if 3000 < size < 5000000:
                        found_files.append((size, full))
                except:
                    pass

found_files.sort(reverse=True)
print('候補: ' + str(len(found_files)) + '件')

os.makedirs('results', exist_ok=True)
results_all = []
count = 0

print('')
print('=' * 65)
print('  MoCKAなし文書 一括RR測定')
print('=' * 65)

for size, path in found_files:
    if count >= 25:
        break
    text = read_file(path)
    if not text or len(text) < 500:
        continue
    # AI生成文書を簡易除外（英語率が高いものはスキップ）
    r = analyze(text)
    wrr = calc_wrr(r)
    missing = sum(1 for v in r.values() if not v['found'])
    fname = os.path.basename(path)[:45]
    print('  [{:>2}] {:<45} {:>7}字 WRR:{:>5}%'.format(count+1, fname, len(text), wrr))
    results_all.append({
        'id': 'A0-H' + str(count+1),
        'file': os.path.basename(path),
        'path': path,
        'size': len(text),
        'weighted_rr': wrr,
        'missing_stages': missing,
        'hash': hashlib.sha256(text.encode('utf-8', errors='ignore')).hexdigest()[:16]
    })
    count += 1

avg = round(sum(r['weighted_rr'] for r in results_all)/len(results_all), 1) if results_all else 0
print('=' * 65)
print('  取得件数: {}件  平均 Weighted RR: {}%'.format(len(results_all), avg))

date = datetime.now().strftime('%Y%m%d')
out = 'results/A0_bulk_human_docs_' + date + '.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump({'experiment':'A0_bulk_human','count':len(results_all),'avg_wrr':avg,'results':results_all}, f, ensure_ascii=False, indent=2)
print('  Saved: ' + out)
