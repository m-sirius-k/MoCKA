import json
import os

MODEL_FILE = "repair_strategy_model.json"
THEORY_FILE = "civilization_theory.json"

def load_model():

    if not os.path.exists(MODEL_FILE):
        return None

    with open(MODEL_FILE,"r") as f:
        return json.load(f)

def generate_theory(model):

    best = None
    best_score = -1

    for rid,data in model.items():

        attempts = data.get("attempts",0)
        success = data.get("success",0)

        if attempts == 0:
            continue

        score = success/attempts

        if score > best_score:
            best_score = score
            best = rid

    return {
        "dominant_strategy":best,
        "confidence":best_score
    }

def run():

    model = load_model()

    if not model:
        print("NO_MODEL")
        return

    theory = generate_theory(model)

    with open(THEORY_FILE,"w") as f:
        json.dump(theory,f,indent=2)

    print("CIVILIZATION_THEORY_UPDATED")
    print("dominant_strategy:",theory["dominant_strategy"])

if __name__ == "__main__":
    run()
