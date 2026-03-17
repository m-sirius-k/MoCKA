import json
import os
from hash_utils import compute_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ledger_path = os.path.join(BASE_DIR, "runtime", "main", "ledger.json")

with open(ledger_path, "r", encoding="utf-8") as f:
    ledger = json.load(f)

prev_hash = "GENESIS"

for i, event in enumerate(ledger):
    if event["prev_hash"] != prev_hash:
        print("CHAIN BROKEN AT", i)
        exit(1)

    expected_hash = compute_hash(event)

    if event["event_hash"] != expected_hash:
        print("HASH INVALID AT", i)
        exit(1)

    prev_hash = event["event_hash"]

print("CHAIN VERIFIED", len(ledger), "events")
