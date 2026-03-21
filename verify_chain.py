import json
from runtime.hash_utils import compute_hash
from runtime.schema_validator import validate_event
from runtime.env_guard import enforce_env

enforce_env("verify")

ledger_path = "runtime/main/ledger.json"

with open(ledger_path, "r", encoding="utf-8") as f:
    ledger = json.load(f)

prev = "0"

for i, event in enumerate(ledger):
    validate_event(event)

    h = compute_hash(event)

    if h != event["hash"]:
        print(f"HASH INVALID AT {i}")
        exit(1)

    if event["prev_hash"] != prev:
        print(f"CHAIN INVALID AT {i}")
        exit(1)

    prev = h

print(f"CHAIN VERIFIED {len(ledger)} events")
