import json
import hashlib
import time

LEDGER="runtime/main/ledger.json"

def sha256(x):
    return hashlib.sha256(x.encode()).hexdigest()

def load():
    with open(LEDGER,"r",encoding="utf-8") as f:
        return json.load(f)

def save(d):
    with open(LEDGER,"w",encoding="utf-8") as f:
        json.dump(d,f,indent=2)

def main():

    ledger=load()

    last=ledger[-1]

    eid=last["event_id"]+1

    lamport=last.get("lamport",0)+1

    ts=int(time.time())

    payload={
        "node":"node_local",
        "status":"alive"
    }

    prev=last["event_hash"]

    data=str(eid)+str(ts)+"node_heartbeat"+str(payload)+prev

    h=sha256(data)

    ev={
        "event_id":eid,
        "lamport":lamport,
        "timestamp":ts,
        "type":"node_heartbeat",
        "payload":payload,
        "prev_hash":prev,
        "event_hash":h
    }

    ledger.append(ev)

    save(ledger)

    print("NODE HEARTBEAT WRITTEN")

if __name__=="__main__":
    main()
