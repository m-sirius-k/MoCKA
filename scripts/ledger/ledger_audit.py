import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿import json
import hashlib

LEDGER="runtime/main/ledger.json"

def h(x):
    return hashlib.sha256(x.encode()).hexdigest()

with open(LEDGER,"r",encoding="utf-8") as f:
    d=json.load(f)

ok=True

for i in range(1,len(d)):

    prev=d[i]["prev_hash"]

    calc=d[i-1]["event_hash"]

    if prev!=calc:
        ok=False
        print("CHAIN BROKEN AT",i)

if ok:
    print("LEDGER AUDIT OK",len(d),"events")
