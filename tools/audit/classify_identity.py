import json
from collections import Counter

path="data/decisions/decision_ledger.jsonl"

classes=Counter()

def classify(a):
    if "PENDING" in a:
        return "PENDING"
    if "Claude" in a:
        return "VERIFICATION_ACTOR"
    if "くろこ" in a or "代理" in a or "via" in a:
        return "EXECUTION_PROXY"
    if "Human Gate" in a:
        return "HUMAN_GATE"
    if "きむら博士" in a or "nsjp_kimura" in a:
        return "HUMAN_AUTHORITY"
    return "OTHER"

with open(path,encoding="utf-8") as f:
    for line in f:
        obj=json.loads(line)
        a=obj.get("approved_by","")
        classes[classify(a)] += 1

print(classes)
