import json
import hashlib
import time

ledger_path = "runtime/main/ledger.json"

def verify():

    with open(ledger_path,"r") as f:
        ledger = json.load(f)

    for i in range(1,len(ledger)):

        prev = ledger[i-1]
        cur = ledger[i]

        if cur["prev_hash"] != prev["event_hash"]:
            print("ALERT CHAIN BREAK",i)
            return

        raw = cur.copy()
        event_hash = raw.pop("event_hash")

        check = hashlib.sha256(
            json.dumps(raw,sort_keys=True).encode()
        ).hexdigest()

        if check != event_hash:
            print("ALERT HASH INVALID",i)
            return

    print("SHADOW OK",len(ledger),"events")


while True:

    verify()

    time.sleep(5)
