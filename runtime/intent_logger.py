import json
import os
from datetime import datetime, UTC

LEDGER_PATH = "intent_ledger.json"

def append_intent(intent):
    if not intent:
        return

    record = {
        "event_type": "INTENT_RECEIVED",
        "intent_id": intent["intent_id"],
        "source": intent["source"],
        "timestamp": datetime.now(UTC).isoformat(),
        "goal": intent["goal"]
    }

    if not os.path.exists(LEDGER_PATH):
        ledger = []
    else:
        with open(LEDGER_PATH, "r", encoding="utf-8") as f:
            ledger = json.load(f)

    ledger.append(record)

    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(ledger, f, ensure_ascii=False, indent=2)

    print("INTENT LOGGED")
