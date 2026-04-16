import json
from pathlib import Path

data = json.loads(Path(r'C:\Users\sirok\MoCKA\data\experiments\incidents_candidates.json').read_text('utf-8'))
for c in data['candidates']:
    if c['score'] >= 5:
        print('='*50)
        print(f"file  : {c['file'][:40]}")
        print(f"source: {c['source']}  score: {c['score']}")
        print(f"keys  : {c['matched_keywords']}")
        print(f"excerpt:\n{c['excerpt']}")
        print()
