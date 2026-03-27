import json

path = "runtime/main/ledger.json"

with open(path, "r", encoding="utf-8") as f:
    ledger = json.load(f)

# 1件目を改ざん
ledger[0]["data"]["tampered"] = True

with open(path, "w", encoding="utf-8") as f:
    json.dump(ledger, f, ensure_ascii=False, indent=2)

print("TAMPERED")
