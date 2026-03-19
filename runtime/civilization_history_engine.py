import json
import os
from datetime import datetime

CONSENSUS_FILE="civilization_consensus.json"
MODEL_FILE="repair_strategy_model.json"
HISTORY_FILE="mocka_civilization_history.json"

def load(path):

    if not os.path.exists(path):
        return None

    with open(path,"r",encoding="utf-8-sig") as f:
        return json.load(f)

def load_history():

    if not os.path.exists(HISTORY_FILE):
        return []

    with open(HISTORY_FILE,"r",encoding="utf-8-sig") as f:
        return json.load(f)

def save(data):

    with open(HISTORY_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)

def main():

    consensus=load(CONSENSUS_FILE)
    model=load(MODEL_FILE)

    history=load_history()

    record={
        "timestamp":datetime.now().isoformat(),
        "consensus":consensus,
        "model":model
    }

    history.append(record)

    save(history)

    print("CIVILIZATION_HISTORY_RECORDED")

if __name__=="__main__":
    main()
