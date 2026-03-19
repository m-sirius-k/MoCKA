import json
import os

MODEL_FILE = "repair_strategy_model.json"
FITNESS_FILE = "strategy_fitness.json"

def load_model():
    if not os.path.exists(MODEL_FILE):
        print("MODEL_NOT_FOUND")
        return None
    with open(MODEL_FILE,"r") as f:
        return json.load(f)

def compute_fitness(data):

    attempts = data.get("attempts",0)
    success = data.get("success",0)

    if attempts == 0:
        return 0

    return round(success / attempts,3)

def run():

    model = load_model()

    if not model:
        return

    fitness = {}

    for rid,data in model.items():

        fitness[rid] = {
            "fitness": compute_fitness(data),
            "attempts": data.get("attempts",0),
            "success": data.get("success",0),
            "fail": data.get("fail",0)
        }

    with open(FITNESS_FILE,"w") as f:
        json.dump(fitness,f,indent=2)

    print("FITNESS_UPDATED")
    print("strategies:",len(fitness))

if __name__ == "__main__":
    run()
