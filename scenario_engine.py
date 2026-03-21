import json
import os
import time
import hashlib

BASE_DIR = r"C:\Users\sirok\MoCKA"
BRANCH_DIR = os.path.join(BASE_DIR,"runtime","branches")

def load(path):
    with open(path,"r",encoding="utf-8") as f:
        return json.load(f)

def save(path,data):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)

def hash_event(event):
    return hashlib.sha256(json.dumps(event,sort_keys=True).encode()).hexdigest()

print("=== MoCKA Scenario Engine ===")

branch = input("branch id: ")

ledger_path = os.path.join(BRANCH_DIR,branch,"ledger.json")

if not os.path.exists(ledger_path):
    print("branch not found")
    exit()

ledger = load(ledger_path)

scenario = [
    {"type":"network_partition","payload":{"node":"node_local"}},
    {"type":"leader_election","payload":{"candidate":"node_local"}},
    {"type":"node_recovery","payload":{"node":"node_local"}}
]

for s in scenario:

    prev_hash = ledger[-1]["event_hash"]

    event = {
        "event_id": ledger[-1]["event_id"] + 1,
        "timestamp": int(time.time()),
        "type": s["type"],
        "payload": s["payload"],
        "prev_hash": prev_hash
    }

    event["event_hash"] = hash_event(event)

    ledger.append(event)

save(ledger_path,ledger)

print("")
print("scenario injected")
print("events added:",len(scenario))
