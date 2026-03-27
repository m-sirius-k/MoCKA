# ============================================
# MoCKA Timeline Promotion Engine
# best timeline を main world_state に昇格
# ============================================

import json
import os
import time

BEST_FILE = "runtime/best_timeline.json"
MAIN_STATE = "runtime/world_state.json"
PROMOTION_LOG = "runtime/promoted_branches.json"


def load_best():

    with open(BEST_FILE,"r",encoding="utf-8") as f:
        return json.load(f)


def save_main_state(state):

    with open(MAIN_STATE,"w",encoding="utf-8") as f:
        json.dump(state,f,indent=2)


def append_promotion(branch,fitness):

    if os.path.exists(PROMOTION_LOG):

        with open(PROMOTION_LOG,"r",encoding="utf-8") as f:
            data = json.load(f)

    else:

        data = []

    data.append({
        "timestamp": int(time.time()),
        "branch": branch,
        "fitness": fitness
    })

    with open(PROMOTION_LOG,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)


if __name__ == "__main__":

    best = load_best()

    branch = best["branch"]
    fitness = best["fitness"]
    state = best["state"]

    save_main_state(state)

    append_promotion(branch,fitness)

    print("PROMOTED BRANCH")
    print(branch)
