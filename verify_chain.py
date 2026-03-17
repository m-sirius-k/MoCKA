import json
import hashlib
from pathlib import Path

LEDGER_PATH = Path(__file__).parent / "runtime" / "main" / "ledger.json"

if not LEDGER_PATH.exists():
    raise FileNotFoundError(f"Ledger not found: {LEDGER_PATH}")

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

    expected_prev = entry_copy.pop("prev_hash", None)
    stored_hash = entry_copy.pop("hash", None)

    if i == 0:
        # GENESISは検証スキップ（ここが重要）
        prev_hash = stored_hash
        continue

    if expected_prev != prev_hash:
        raise Exception(f"CHAIN BREAK at {i}: prev mismatch")

    payload = canonical(entry_copy)
    computed_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    if computed_hash != stored_hash:
        raise Exception(f"HASH MISMATCH at {i}")

    prev_hash = computed_hash

print(f"CHAIN VERIFIED {len(ledger)} events")
