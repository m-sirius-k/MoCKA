import json

path="data/decisions/decision_ledger.jsonl"

targets=["Claude","PENDING","代理","くろこ","R01"]

with open(path,encoding="utf-8") as f:
    for line in f:
        obj=json.loads(line)
        a=obj.get("approved_by","")
        if any(t in a for t in targets):
            print("="*80)
            print("decision_id:", obj.get("decision_id"))
            print("title:", obj.get("title"))
            print("approved_by:", a)
            print("status:", obj.get("status"))
