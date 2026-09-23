import json
path = 'data/decisions/decision_ledger.jsonl'
with open(path, encoding='utf-8') as f:
    lines = [json.loads(line) for line in f if line.strip()]

d = lines[0]
alts = d.get('alternatives', [])
print(f"Sample alternatives: {alts}")
print(f"\nAlternatives schema check:")
if alts and isinstance(alts, list):
    print(f"  First alternative: {alts[0]}")
    print(f"  Has 'option': {'option' in alts[0]}")
    print(f"  Has 'rejected_reason': {'rejected_reason' in alts[0]}")

print(f"\nStatus values in ledger: {set(d.get('status') for d in lines if 'status' in d)}")

print(f"\nCan alternatives store non-rejected decisions?")
print(f"  Current: 'option' + 'rejected_reason' (implies rejection)")
print(f"  For REM: Would need 'adopted' or 'evidence_only' status")
print(f"  Status is MISSING in alternatives array (gap)")
