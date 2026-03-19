import json
import os

MODEL_FILE = "repair_strategy_model.json"
SELECT_FILE = "selected_repair_strategy.json"


def load_model():

    if not os.path.exists(MODEL_FILE):
        print("MODEL_NOT_FOUND")
        return None

    with open(MODEL_FILE,"r") as f:
        return json.load(f)


def compute_score(strategy):

    attempts = strategy.get("attempts",0)
    success = strategy.get("success",0)

    if attempts == 0:
        return 0

    return success / attempts


def select_best(model):

    best_id = None
    best_score = -1

    for rid, data in model.items():

        score = compute_score(data)

        if score > best_score:
            best_score = score
            best_id = rid

    return best_id, best_score


def run():

    model = load_model()

    if not model:
        return

    rid, score = select_best(model)

    result = {
        "selected_strategy": rid,
        "score": score
    }

    with open(SELECT_FILE,"w") as f:
        json.dump(result,f,indent=2)

    print("BEST_STRATEGY_SELECTED")
    print("strategy:",rid)
    print("score:",score)


if __name__ == "__main__":
    run()
