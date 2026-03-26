import json
import hashlib
import os

# ★ここを修正（runtime/main → runtime）
LEDGER_PATH = "runtime/ledger.json"

def load():
    if not os.path.exists(LEDGER_PATH):
        return []
    with open(LEDGER_PATH,"r",encoding="utf-8-sig") as f:
        return json.load(f)

def hash_event(ev):
    data = {
        "type": ev.get("type"),
        "action": ev.get("action"),
        "ts": ev.get("ts")
    }
    s = json.dumps(data, sort_keys=True)
    return hashlib.sha256(s.encode()).hexdigest()

def main():
    ledger = load()

    if not ledger:
        print("EMPTY LEDGER")
        return

    prev_hash = None

    for i, ev in enumerate(ledger):
        h = hash_event(ev)

        if i == 0:
            prev_hash = h
            continue

        if ev.get("prev_hash") != prev_hash:
            print("CHAIN BROKEN AT", i)
            return

        prev_hash = h

    print("CHAIN VERIFIED", len(ledger), "events")

if __name__ == "__main__":
    main()
