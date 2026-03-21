import json
import os
import hashlib

BASE = r"C:\Users\sirok\MoCKA"
LEDGER = os.path.join(BASE, "runtime", "main", "ledger.json")

START_VERIFY = 27

def load():
    with open(LEDGER, "r", encoding="utf-8") as f:
        return json.load(f)

def calc_hash(e):
    raw = f"{e['event_id']}{e['timestamp']}{e['payload']}{e['prev_hash']}"
    return hashlib.sha256(raw.encode()).hexdigest()

ledger = load()

prev_hash = None

for e in ledger:

    if "event_id" not in e:
        continue

    if e["event_id"] < START_VERIFY:
        prev_hash = e.get("event_hash", prev_hash)
        continue

    h = calc_hash(e)

    if h != e["event_hash"]:
        print("HASH ERROR", e["event_id"])
        exit()

    if prev_hash and e["prev_hash"] != prev_hash:
        print("CHAIN BREAK", e["event_id"])

    prev_hash = e["event_hash"]

print("LEDGER OK")