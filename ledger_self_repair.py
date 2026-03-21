import json
import hashlib
import time
import os

LEDGER_PATH = r"runtime\main\ledger.json"
STATE_PATH = r"runtime\state.json"

def sha256(data):
    return hashlib.sha256(data.encode()).hexdigest()

def load_ledger():
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_ledger(ledger):
    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2)

def verify_chain(ledger):

    prev_hash = "0"

    for ev in ledger:

        if ev["prev_hash"] != prev_hash:
            return False, ev

        data = str(ev["event_id"]) + str(ev["timestamp"]) + ev["type"] + str(ev["payload"]) + ev["prev_hash"]
        h = sha256(data)

        if h != ev["event_hash"]:
            return False, ev

        prev_hash = ev["event_hash"]

    return True, None


def append_repair_event(ledger, broken_event):

    last = ledger[-1]

    event_id = last["event_id"] + 1
    lamport = last.get("lamport",0) + 1

    payload = {
        "repair_target": broken_event["event_id"],
        "reason": "ledger_integrity_failure",
        "repair_node": "local_node"
    }

    timestamp = int(time.time())

    prev_hash = last["event_hash"]

    data = str(event_id)+str(timestamp)+"repair"+str(payload)+prev_hash
    event_hash = sha256(data)

    repair_event = {
        "event_id": event_id,
        "lamport": lamport,
        "timestamp": timestamp,
        "type": "repair",
        "payload": payload,
        "prev_hash": prev_hash,
        "event_hash": event_hash
    }

    ledger.append(repair_event)

    return ledger


def main():

    ledger = load_ledger()

    ok, broken = verify_chain(ledger)

    if ok:
        print("LEDGER OK")
        return

    print("LEDGER BROKEN at event", broken["event_id"])

    ledger = append_repair_event(ledger, broken)

    save_ledger(ledger)

    print("REPAIR EVENT APPENDED")


if __name__ == "__main__":
    main()

