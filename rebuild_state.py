import json
from runtime.hash_utils import compute_hash
from runtime.auth_guard import enforce_rebuild_permission
from runtime.rebuild_logger import record_rebuild

enforce_rebuild_permission()

ledger_path = "runtime/main/ledger.json"

with open(ledger_path, "r", encoding="utf-8") as f:
    ledger = json.load(f)

prev = "0"
new_ledger = []

for event in ledger:
    e = dict(event)
    e["prev_hash"] = prev
    e["hash"] = compute_hash(e)
    prev = e["hash"]
    new_ledger.append(e)

with open(ledger_path, "w", encoding="utf-8") as f:
    json.dump(new_ledger, f, ensure_ascii=False, indent=2)

# ←ここが核心
record_rebuild()

print(f"LEDGER REBUILT {len(new_ledger)}")
