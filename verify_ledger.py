import json
import hashlib

LEDGER_PATH = "ledger.json"

def sha256(s):
    return hashlib.sha256(s.encode()).hexdigest()

with open(LEDGER_PATH,"r",encoding="utf-8") as f:
    ledger = json.load(f)

for i in range(1,len(ledger)):
    prev = ledger[i-1]
    curr = ledger[i]

    if curr["prev_hash"] != prev["hash"]:
        print("CHAIN BROKEN AT", i)
        exit()

    calc = sha256(json.dumps({
        k:curr[k] for k in curr if k!="hash"
    }, sort_keys=True))

    if calc != curr["hash"]:
        print("HASH INVALID AT", i)
        exit()

print("LEDGER VERIFIED")
