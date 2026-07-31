import json

path="data/decisions/decision_ledger.jsonl"

with open(path,encoding="utf-8") as f:
    for line in f:
        obj=json.loads(line)
        a=obj.get("approved_by","")
        if a and not any(x in a for x in [
            "PENDING",
            "Claude",
            "くろこ",
            "代理",
            "via",
            "Human Gate",
            "きむら博士",
            "nsjp_kimura"
        ]):
            print(obj.get("decision_id"))
            print(obj.get("title"))
            print(a)
