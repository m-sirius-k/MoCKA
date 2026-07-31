import json

path="data/decisions/decision_ledger.jsonl"

with open(path,encoding="utf-8") as f:
    for line in f:
        obj=json.loads(line)
        a=obj.get("approved_by","")
        if "Human Gate" in a:
            print(obj.get("decision_id"), "|", a)
