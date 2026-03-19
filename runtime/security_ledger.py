import json, time, os

LEDGER_PATH = "runtime/main/security_ledger.json"

def log(event):
    os.makedirs("runtime/main",exist_ok=True)
    if not os.path.exists(LEDGER_PATH):
        data = []
    else:
        with open(LEDGER_PATH,"r",encoding="utf-8") as f:
            data = json.load(f)

    data.append({
        "ts": int(time.time()),
        "event": event
    })

    with open(LEDGER_PATH,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)

if __name__ == "__main__":
    log("init")
