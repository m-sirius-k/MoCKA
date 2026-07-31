import json

path="data/decisions/decision_ledger.jsonl"

with open(path,encoding="utf-8") as f:
    for line in f:
        obj=json.loads(line)
        if obj.get("decision_id") in ["DC_20260712_008","DC_20260712_010"]:
            print("="*60)
            print(json.dumps(obj,ensure_ascii=False,indent=2))
