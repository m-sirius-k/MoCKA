import json
from pathlib import Path
import random

BRANCH_DIR = Path("runtime/branches")

EVENT_TYPES = [
    "economic_change",
    "node_failure",
    "network_recovery",
    "policy_update",
    "resource_shift"
]

def load_json(p):
    with open(p,"r",encoding="utf-8") as f:
        return json.load(f)

def mutation_bias():

    scores = {}

    for branch in BRANCH_DIR.iterdir():

        m = branch / "metrics.json"
        if not m.exists():
            continue

        metrics = load_json(m)
        fit = metrics.get("fitness",0)

        for e in EVENT_TYPES:
            scores.setdefault(e,0)

        # fitness が高い branch の mutation を強化
        for e in EVENT_TYPES:
            scores[e] += fit * random.random()

    return scores


def choose_mutation():

    scores = mutation_bias()

    if not scores:
        return random.choice(EVENT_TYPES)

    best = max(scores,key=scores.get)

    return best


if __name__ == "__main__":

    m = choose_mutation()

    print("chosen mutation:",m)
