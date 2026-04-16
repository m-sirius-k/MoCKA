import json
import hashlib

LEDGER_PATH = "ledger.json"

def calc_hash(prev_hash, data):
    d = dict(data)
    d.pop("hash", None)
    raw = prev_hash + json.dumps(d, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()

def verify_chain():
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        ledger = json.load(f)

    prev_hash = "GENESIS"

    for i, entry in enumerate(ledger):
        expected = calc_hash(prev_hash, entry)

        if entry["hash"] != expected:
            print("INVALID AT", i)
            return

        prev_hash = entry["hash"]

    print("CHAIN VERIFIED", len(ledger), "events")

if __name__ == "__main__":
    verify_chain()
