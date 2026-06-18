import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿import json
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
