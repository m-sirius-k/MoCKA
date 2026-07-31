import json
from collections import Counter

path = "data/decisions/decision_ledger.jsonl"

approved = Counter()

with open(path, encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        if "approved_by" in obj:
            approved[obj["approved_by"]] += 1

print(approved)
