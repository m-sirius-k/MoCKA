import json
import os
from datetime import datetime

VERIFY_FILE="repair_verification.json"
MODEL_FILE="repair_strategy_model.json"
STATE_FILE="mocka_node_state.json"

def load(path):

    if not os.path.exists(path):
        return None

    with open(path,"r",encoding="utf-8-sig") as f:
        return json.load(f)

def main():

    verify=load(VERIFY_FILE)
    model=load(MODEL_FILE)

    state={
        "node":"mocka-node-1",
        "timestamp":datetime.now().isoformat(),
        "runtime_status":verify,
        "repair_model":model
    }

    with open(STATE_FILE,"w",encoding="utf-8") as f:
        json.dump(state,f,indent=2)

    print("NODE_STATE_EXPORTED")

if __name__=="__main__":
    main()
