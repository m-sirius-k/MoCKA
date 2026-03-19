import json
import os

MODEL_FILE = "repair_strategy_model.json"
FITNESS_FILE = "strategy_fitness.json"

MIN_ATTEMPTS = 3
MIN_FITNESS = 0.2


def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path,"r") as f:
        return json.load(f)


def run():

    model = load_json(MODEL_FILE)
    fitness = load_json(FITNESS_FILE)

    if not model or not fitness:
        print("DATA_MISSING")
        return

    removed = []

    for rid,data in list(fitness.items()):

        attempts = data.get("attempts",0)
        score = data.get("fitness",0)

        if attempts >= MIN_ATTEMPTS and score < MIN_FITNESS:
            removed.append(rid)
            model.pop(rid,None)

    with open(MODEL_FILE,"w") as f:
        json.dump(model,f,indent=2)

    print("POPULATION_CONTROL_COMPLETE")
    print("removed:",removed)
    print("remaining:",len(model))


if __name__ == "__main__":
    run()
