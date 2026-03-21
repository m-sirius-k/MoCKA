import json
import time
import os

LEDGER="runtime/main/ledger.json"
SNAPDIR="runtime/snapshots"

with open(LEDGER,"r",encoding="utf-8") as f:
    d=json.load(f)

if len(d)<20:
    print("NOT ENOUGH EVENTS")
    exit()

cut=len(d)//2

snap=d[:cut]
rest=d[cut:]

ts=int(time.time())

snapfile=f"{SNAPDIR}/ledger_comp_{ts}.json"

with open(snapfile,"w",encoding="utf-8") as f:
    json.dump(snap,f,indent=2)

with open(LEDGER,"w",encoding="utf-8") as f:
    json.dump(rest,f,indent=2)

print("LEDGER COMPRESSED")
print("snapshot:",snapfile)
print("remaining events:",len(rest))
