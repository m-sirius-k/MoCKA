import json
from pathlib import Path
path = Path('data/decisions/decision_ledger.jsonl')
lines = list(open(path, 'r', encoding='utf-8'))
print(f'Total decisions: {len(lines)}')
for i in range(max(0, len(lines)-3), len(lines)):
    d = json.loads(lines[i])
    fields = list(d.keys())
    did = d.get('decision_id', '')
    print(f'\nDecision {did}: {len(fields)} fields')
    print(f'  Fields: {sorted(fields)}')
    print(f'  Has request_id: {"request_id" in fields}')
    print(f'  Has execution_id: {"execution_id" in fields}')
