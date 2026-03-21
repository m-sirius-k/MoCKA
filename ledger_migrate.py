import json
import hashlib
import time

LEDGER = r"runtime\main\ledger.json"

def sha256(x):
    import hashlib
    return hashlib.sha256(x.encode()).hexdigest()

def load():
    with open(LEDGER,"r",encoding="utf-8") as f:
        return json.load(f)

def save(l):
    with open(LEDGER,"w",encoding="utf-8") as f:
        json.dump(l,f,indent=2)

def migrate(ledger):

    new=[]
    prev="0"
    eid=0
    lamport=0

    for e in ledger:

        if "event_id" not in e:

            payload={"legacy_event":e}

            ts=int(time.time())

            data=str(eid)+str(ts)+"legacy_event"+str(payload)+prev
            h=sha256(data)

            ne={
                "event_id":eid,
                "lamport":lamport,
                "timestamp":ts,
                "type":"legacy_event",
                "payload":payload,
                "prev_hash":prev,
                "event_hash":h
            }

        else:

            ne=e

        new.append(ne)

        prev=ne["event_hash"]
        eid+=1
        lamport+=1

    return new

def main():

    l=load()

    nl=migrate(l)

    save(nl)

    print("LEDGER MIGRATED")

if __name__=="__main__":
    main()
