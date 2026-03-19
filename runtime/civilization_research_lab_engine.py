import json
import os
import random
import time

MODEL_FILE = "repair_strategy_model.json"
LAB_LOG_FILE = "civilization_research_lab_log.json"

def load_model():
    if not os.path.exists(MODEL_FILE):
        return None
    with open(MODEL_FILE,"r") as f:
        return json.load(f)

def load_log():
    if not os.path.exists(LAB_LOG_FILE):
        return []
    with open(LAB_LOG_FILE,"r") as f:
        return json.load(f)

def run_experiment(model):

    strategies = list(model.keys())

    if not strategies:
        return None

    base = random.choice(strategies)

    simulated_success = random.random() < 0.35

    return {
        "base_strategy":base,
        "experiment_success":simulated_success
    }

def run():

    model = load_model()

    if not model:
        print("NO_STRATEGY_MODEL")
        return

    log = load_log()

    result = run_experiment(model)

    if not result:
        print("NO_EXPERIMENT")
        return

    entry = {
        "timestamp":int(time.time()),
        "base_strategy":result["base_strategy"],
        "success":result["experiment_success"]
    }

    log.append(entry)

    with open(LAB_LOG_FILE,"w") as f:
        json.dump(log,f,indent=2)

    print("RESEARCH_LAB_EXPERIMENT_COMPLETE")
    print("strategy:",result["base_strategy"])
    print("success:",result["experiment_success"])

if __name__ == "__main__":
    run()
