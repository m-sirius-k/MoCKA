import json
import hashlib

LEDGER=r"runtime\main\ledger.json"

def sha256(x):
    import hashlib
    return hashlib.sha256(x.encode()).hexdigest()

def load():
    with open(LEDGER,"r",encoding="utf-8") as f:
        return json.load(f)

def save(l):
    with open(LEDGER,"w",encoding="utf-8") as f:
        json.dump(l,f,indent=2)

def normalize(ledger):

    prev="0"

    for i,e in enumerate(ledger):

        e["event_id"]=i

        payload=e.get("payload","")

        ts=e.get("timestamp",0)

        typ=e.get("type","unknown")

        data=str(i)+str(ts)+typ+str(payload)+prev

        h=sha256(data)

        e["prev_hash"]=prev
        e["event_hash"]=h

        prev=h

    return ledger

def main():

    l=load()

    l=normalize(l)

    save(l)

    print("LEDGER NORMALIZED")

if __name__=="__main__":
    main()
