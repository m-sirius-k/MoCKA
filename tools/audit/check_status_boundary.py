import json
from collections import Counter

path="data/decisions/decision_ledger.jsonl"

counter=Counter()

with open(path,encoding="utf-8") as f:
    for line in f:
        obj=json.loads(line)
        a=obj.get("approved_by","")
        status=obj.get("status","")
        
        if "PENDING" in a:
            counter["PENDING_status_"+status]+=1
        if "Claude" in a:
            counter["Claude_status_"+status]+=1
        if "Human Gate" in a:
            counter["HumanGate_status_"+status]+=1

print(counter)
