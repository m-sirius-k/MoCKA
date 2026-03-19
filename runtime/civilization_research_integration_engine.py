import json
import os

LAB_FILE = "civilization_research_lab_log.json"
MODEL_FILE = "repair_strategy_model.json"

def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path,"r") as f:
        return json.load(f)

def run():

    lab = load_json(LAB_FILE)
    model = load_json(MODEL_FILE)

    if not lab or not model:
        print("NO_DATA")
        return

    last = lab[-1]

    strategy = last["base_strategy"]
    success = last["success"]

    if strategy not in model:
        print("UNKNOWN_STRATEGY")
        return

    model[strategy]["attempts"] += 1

    if success:
        model[strategy]["success"] += 1
    else:
        model[strategy]["fail"] += 1

    with open(MODEL_FILE,"w") as f:
        json.dump(model,f,indent=2)

    print("RESEARCH_RESULT_INTEGRATED")
    print("strategy:",strategy)
    print("success:",success)

if __name__ == "__main__":
    run()
