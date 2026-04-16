import json
from pathlib import Path

d = Path(r'C:\Users\sirok\MoCKA\data\storage\infield\REDUCING')
files = sorted(d.glob('*.json'))
for f in files[:10]:
    try:
        data = json.loads(f.read_text('utf-8'))
        rate = data.get('restore_rate', 0)
        src  = data.get('source', '')
        print(f'{f.name[:40]} rate={rate:.2f} src={src}')
    except Exception as e:
        print(f'{f.name[:40]} ERROR: {e}')
