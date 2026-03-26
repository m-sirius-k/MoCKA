import json
import os
import hashlib

BASE = r"C:\Users\sirok\MoCKA"
LEDGER = os.path.join(BASE, "runtime", "main", "ledger.json")

def load():
    with open(LEDGER, "r", encoding="utf-8") as f:
        return json.load(f)

def calc_hash(e):
    raw = f"{e['event_id']}{e['timestamp']}{e['type']}{e['action']}{e['prev_hash']}"
    return hashlib.sha256(raw.encode()).hexdigest()

ledger = load()
prev_hash = "0" * 64
errors = 0

for e in ledger:
    if "event_id" not in e:
        continue
    h = calc_hash(e)
    if h != e["event_hash"]:
        print("HASH ERROR", e["event_id"])
        errors += 1
    if e["prev_hash"] != prev_hash:
        print("CHAIN BREAK", e["event_id"])
        errors += 1
    prev_hash = e["event_hash"]

if errors == 0:
    print("LEDGER OK")
else:
    print(f"ERRORS: {errors}")
