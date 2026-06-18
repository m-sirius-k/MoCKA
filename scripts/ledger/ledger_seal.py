import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿import json
import hashlib

ledger_path = "runtime/main/ledger.json"

with open(ledger_path,"r") as f:
    ledger = json.load(f)

chain = ""

for e in ledger:
    chain += e["event_hash"]

seal = hashlib.sha256(chain.encode()).hexdigest()

print("LEDGER EVENTS:",len(ledger))
print("LEDGER SEAL :",seal)
