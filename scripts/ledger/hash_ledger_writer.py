import json
import os
import time
import hashlib

PATH = "runtime/ledger.json"

def load():
    if not os.path.exists(PATH):
        return []
    with open(PATH,"r",encoding="utf-8-sig") as f:
        return json.load(f)

def save(d):
    with open(PATH,"w",encoding="utf-8") as f:
        json.dump(d,f,indent=2)

def hash_event(ev):
    data = {
        "type": ev["type"],
        "action": ev["action"],
        "ts": ev["ts"]
    }
    s = json.dumps(data, sort_keys=True)
    return hashlib.sha256(s.encode()).hexdigest()

def main():
    ledger = load()

    ev = {
        "type":"AUTO",
        "action":"HEARTBEAT",
        "ts":time.time()
    }

    if ledger:
        prev = ledger[-1]
        ev["prev_hash"] = hash_event(prev)
    else:
        ev["prev_hash"] = None

    ledger.append(ev)
    save(ledger)

    print("LEDGER APPENDED", len(ledger))

if __name__=="__main__":
    main()
