import json
import os
import random

MODEL_FILE = "repair_strategy_model.json"

def load_model():

    if not os.path.exists(MODEL_FILE):
        print("MODEL_NOT_FOUND")
        return None

    with open(MODEL_FILE,"r") as f:
        return json.load(f)

def mutate_strategy(model):

    base = random.choice(list(model.keys()))

    new_id = "R" + str(random.randint(100,999))

    model[new_id] = {
        "attempts":0,
        "success":0,
        "fail":0,
        "parent":base
    }

    return new_id

def run():

    model = load_model()

    if not model:
        return

    new_id = mutate_strategy(model)

    with open(MODEL_FILE,"w") as f:
        json.dump(model,f,indent=2)

    print("STRATEGY_MUTATED")
    print("new_strategy:",new_id)

if __name__ == "__main__":
    run()
