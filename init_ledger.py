import json
import hashlib
import time
import os

LEDGER_PATH = "ledger.json"

def sha256(s):
    return hashlib.sha256(s.encode()).hexdigest()

# 初期ブロック（Genesis）
if not os.path.exists(LEDGER_PATH):
    genesis = {
        "index": 0,
        "time": int(time.time()),
        "event": "GENESIS",
        "prev_hash": "0"*64,
    }
    genesis["hash"] = sha256(json.dumps(genesis, sort_keys=True))
    
    with open(LEDGER_PATH,"w",encoding="utf-8") as f:
        json.dump([genesis],f,indent=2)

    print("LEDGER INITIALIZED")
else:
    print("LEDGER EXISTS")
