import json
import os
import time

STATE_PATH = "runtime/state.json"
LEDGER_PATH = "runtime/ledger.json"

def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path,"r",encoding="utf-8-sig") as f:
            return json.load(f)
    except:
        return default

def save_json(path,data):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)

def main():
    state = load_json(STATE_PATH,{})
    ledger = load_json(LEDGER_PATH,[])

    decision = {
        "type": "DECISION",
        "ts": time.time(),
        "action": state.get("last_actions",[])
    }

    ledger.append(decision)

    save_json(LEDGER_PATH,ledger)

    print("DECISION RECORDED:", decision["action"])

if __name__ == "__main__":
    main()
