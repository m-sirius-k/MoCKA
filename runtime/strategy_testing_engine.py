import json
import os
import random

MODEL_FILE = "repair_strategy_model.json"
SELECT_FILE = "selected_repair_strategy.json"

def load_model():
    if not os.path.exists(MODEL_FILE):
        return None
    with open(MODEL_FILE,"r") as f:
        return json.load(f)

def load_selected():
    if not os.path.exists(SELECT_FILE):
        return None
    with open(SELECT_FILE,"r") as f:
        return json.load(f)

def simulate_result():
    return random.random() < 0.3

def run():

    model = load_model()
    selected = load_selected()

    if not model or not selected:
        print("MISSING_DATA")
        return

    sid = selected["selected_strategy"]

    result = simulate_result()

    model[sid]["attempts"] += 1

    if result:
        model[sid]["success"] += 1
        print("STRATEGY_TEST_SUCCESS")
    else:
        model[sid]["fail"] += 1
        print("STRATEGY_TEST_FAIL")

    with open(MODEL_FILE,"w") as f:
        json.dump(model,f,indent=2)

if __name__ == "__main__":
    run()
