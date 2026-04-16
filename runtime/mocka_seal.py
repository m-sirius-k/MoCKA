import json
import hashlib
import os
from datetime import datetime

LEDGER_PATH = "runtime/ledger.json"

def calculate_hash(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

def load_ledger():
    if not os.path.exists(LEDGER_PATH):
        return []
    try:
        with open(LEDGER_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_ledger(ledger):
    os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(ledger, f, ensure_ascii=False, indent=2)

def seal_event(event):
    ledger = load_ledger()

    prev_hash = ledger[-1]["hash"] if ledger else "GENESIS"

    record = {
        "ts": datetime.now().isoformat(),
        "event": event,
        "prev_hash": prev_hash
    }

    record["hash"] = calculate_hash(record)

    ledger.append(record)
    save_ledger(ledger)

    print("SEALED:", record["hash"])
    return record
