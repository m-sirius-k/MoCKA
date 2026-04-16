# drift_logger.py
# Phase5-B1: 予兆をLedgerへ記録

import json
import os
from datetime import datetime, UTC
import uuid

DRIFT_STATE_PATH = r"C:\Users\sirok\MoCKA\runtime\state\drift_state.json"
LEDGER_PATH = r"C:\Users\sirok\MoCKA\runtime\record\event_log.json"

def load_drift():
    if not os.path.exists(DRIFT_STATE_PATH):
        return None
    with open(DRIFT_STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_ledger():
    if not os.path.exists(LEDGER_PATH):
        return []
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

def save_ledger(data):
    os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def create_event(drift):
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
        "type": "DRIFT_PREDICTION",
        "summary": f"ΔDrift={drift.get('delta_drift')} / {drift.get('status')}",
        "delta_drift": drift.get("delta_drift"),
        "status": drift.get("status")
    }

def main():
    drift = load_drift()
    if drift is None:
        print("[DriftLogger] no drift_state found")
        return

    ledger = load_ledger()
    event = create_event(drift)

    ledger.append(event)
    save_ledger(ledger)

    print(f"[DriftLogger] logged: {event['summary']}")

if __name__ == "__main__":
    main()
