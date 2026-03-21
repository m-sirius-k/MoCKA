import json
import hashlib
import time
import os

ledger_path = "runtime/main/ledger.json"
seal_path = "runtime/seal_registry.json"

# ledger 読み込み
with open(ledger_path,"r") as f:
    ledger = json.load(f)

# chain seal 計算
chain = ""
for e in ledger:
    chain += e["event_hash"]

seal = hashlib.sha256(chain.encode()).hexdigest()

# registry 読み込み（壊れていても復旧）
if not os.path.exists(seal_path):
    seals = []
else:
    try:
        with open(seal_path,"r") as f:
            seals = json.load(f)
    except:
        seals = []

entry = {
    "timestamp": int(time.time()),
    "events": len(ledger),
    "seal": seal
}

seals.append(entry)

with open(seal_path,"w") as f:
    json.dump(seals,f,indent=2)

print("SEAL COMMITTED",seal)
