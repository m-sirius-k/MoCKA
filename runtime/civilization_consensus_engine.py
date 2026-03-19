import json
import os

NETWORK_DIR = "civilization_network"
CONSENSUS_FILE = "civilization_consensus_strategy.json"

def load_network_models():

    models = []

    if not os.path.exists(NETWORK_DIR):
        return models

    for file in os.listdir(NETWORK_DIR):

        if file == "repair_strategy_model.json":

            path = os.path.join(NETWORK_DIR,file)

            with open(path,"r") as f:
                models.append(json.load(f))

    return models


def compute_score(data):

    attempts = data.get("attempts",0)
    success = data.get("success",0)

    if attempts == 0:
        return 0

    return success/attempts


def run():

    models = load_network_models()

    if not models:
        print("NO_NETWORK_MODEL")
        return

    best_strategy = None
    best_score = -1

    for model in models:

        for rid,data in model.items():

            score = compute_score(data)

            if score > best_score:

                best_score = score
                best_strategy = rid

    result = {
        "consensus_strategy":best_strategy,
        "score":best_score
    }

    with open(CONSENSUS_FILE,"w") as f:
        json.dump(result,f,indent=2)

    print("CONSENSUS_COMPUTED")
    print("strategy:",best_strategy)
    print("score:",best_score)


if __name__ == "__main__":
    run()
