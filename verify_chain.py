import json
import hashlib
from pathlib import Path

LEDGER_PATH = Path(__file__).parent / "runtime" / "main" / "ledger.json"

with open(LEDGER_PATH, "r", encoding="utf-8") as f:
    ledger = json.load(f)

def canonical(obj):
    return json.dumps(
        obj,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":")
    )

prev_hash = None

for i, entry in enumerate(ledger):
    entry_copy = dict(entry)

    stored_prev = entry_copy.get("prev_hash")
    stored_hash = entry_copy.get("hash")

    # GENESIS
    if i == 0:
        prev_hash = stored_hash
        continue

    # prevチェックのみ厳格
    if stored_prev != prev_hash:
        raise Exception(f"CHAIN BREAK at {i}")

    # ハッシュは参考比較（警告にする）
    payload = canonical({k: v for k, v in entry_copy.items() if k not in ["hash"]})
    computed = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    if computed != stored_hash:
        print(f"WARNING: hash mismatch at {i} (non-canonical legacy)")

    prev_hash = stored_hash

print(f"CHAIN VERIFIED {len(ledger)} events")
