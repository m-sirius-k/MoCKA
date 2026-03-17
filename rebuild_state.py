import json
import hashlib
from pathlib import Path

LEDGER_PATH = Path(__file__).parent / "runtime" / "main" / "ledger.json"

def canonical(obj):
    return json.dumps(
        obj,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":")
    )

# 仮のデータ読み込み（既存をベースにする）
if LEDGER_PATH.exists():
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        ledger = json.load(f)
else:
    ledger = []

new_ledger = []
prev_hash = None

for i, entry in enumerate(ledger):
    entry_copy = {k: v for k, v in entry.items() if k not in ["hash", "prev_hash"]}

    if i == 0:
        entry_copy["prev_hash"] = None
    else:
        entry_copy["prev_hash"] = prev_hash

    payload = canonical(entry_copy)
    new_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    entry_copy["hash"] = new_hash

    new_ledger.append(entry_copy)
    prev_hash = new_hash

# 保存
LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(LEDGER_PATH, "w", encoding="utf-8") as f:
    json.dump(new_ledger, f, ensure_ascii=False, indent=2)

print(f"LEDGER REBUILT: {len(new_ledger)}")
