import json
from datetime import datetime, timezone
from runtime.hash_utils import compute_hash
from runtime.env_utils import get_env

LEDGER_PATH = "runtime/main/ledger.json"

def now():
    return datetime.now(timezone.utc).isoformat()

def load():
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save(ledger):
    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(ledger, f, ensure_ascii=False, indent=2)

def record_rebuild():
    ledger = load()

    prev_hash = ledger[-1]["hash"] if ledger else "0"
    index = len(ledger)

    event = {
        "index": index,
        "timestamp": now(),
        "event_type": "rebuild",
        "data": {
            "actor": get_env("ROLE"),
            "action": "ledger_rebuild"
        },
        "prev_hash": prev_hash
    }

    event["hash"] = compute_hash(event)

    ledger.append(event)
    save(ledger)

    print("REBUILD EVENT RECORDED")
