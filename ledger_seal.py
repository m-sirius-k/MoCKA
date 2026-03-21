import json
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
