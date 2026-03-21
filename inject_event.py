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

print("=== MoCKA Event Injector ===")

branch = input("branch id: ")

ledger_path = os.path.join(BRANCH_DIR,branch,"ledger.json")

if not os.path.exists(ledger_path):
    print("branch not found")
    exit()

ledger = load(ledger_path)

event_type = input("event type: ")
payload_text = input("payload text: ")

prev_hash = ledger[-1]["event_hash"]

event_id = ledger[-1]["event_id"] + 1

ts = int(time.time())

event = {
    "event_id": event_id,
    "timestamp": ts,
    "type": event_type,
    "payload": {"data": payload_text},
    "prev_hash": prev_hash
}

h = hashlib.sha256(json.dumps(event,sort_keys=True).encode()).hexdigest()

event["event_hash"] = h

ledger.append(event)

save(ledger_path,ledger)

print("")
print("event injected")
print(event)
