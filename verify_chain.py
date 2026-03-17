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
    # === 完全に明示的コピー ===
    entry_copy = {}

    for k, v in entry.items():
        if k not in ["hash"]:
            entry_copy[k] = v

    stored_prev = entry.get("prev_hash")
    stored_hash = entry.get("hash")

    if i == 0:
        prev_hash = stored_hash
        continue

    if stored_prev != prev_hash:
        raise Exception(f"CHAIN BREAK at {i}")

    payload = canonical(entry_copy)
    computed = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    if computed != stored_hash:
        raise Exception(f"HASH MISMATCH at {i}")

    prev_hash = stored_hash

print(f"CHAIN VERIFIED {len(ledger)} events")
