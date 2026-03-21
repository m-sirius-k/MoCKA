import json
import time

LEDGER="runtime/main/ledger.json"
NODEMAP="runtime/node_map.json"

TIMEOUT=90

def load(p):
    with open(p,"r",encoding="utf-8") as f:
        return json.load(f)

def save(p,d):
    with open(p,"w",encoding="utf-8") as f:
        json.dump(d,f,indent=2)

def main():

    ledger=load(LEDGER)
    nodes=load(NODEMAP)

    last_seen={}

    for e in ledger:
        if e.get("type")=="node_heartbeat":
            n=e["payload"]["node"]
            ts=e["timestamp"]
            last_seen[n]=ts

    now=int(time.time())

    for n in nodes["nodes"]:

        nid=n["id"]

        ts=last_seen.get(nid,0)

        if now-ts>TIMEOUT:
            n["status"]="dead"
        else:
            n["status"]="alive"

    save(NODEMAP,nodes)

    print("NODE STATUS UPDATED")

if __name__=="__main__":
    main()
