import os
import json
from pathlib import Path

ROOT = Path("runtime")
MAIN_LEDGER = ROOT / "main" / "ledger.json"
BRANCH_DIR = ROOT / "branches"
PROMOTED_LOG = ROOT / "promoted_branches.json"

PROMOTION_THRESHOLD = 0.5

def load_json(p):
    if not p.exists():
        return []
    with open(p,"r",encoding="utf-8") as f:
        return json.load(f)

def save_json(p,data):
    with open(p,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)

def find_fork(main,branch):

    main_hash = {e["event_hash"] for e in main}

    fork = 0

    for i,e in enumerate(branch):
        if e["event_hash"] in main_hash:
            fork = i+1

    return fork

def find_best_branch():

    promoted = load_json(PROMOTED_LOG)

    best = None
    best_fitness = -999999

    for branch in os.listdir(BRANCH_DIR):

        if branch in promoted:
            continue

        metrics_file = BRANCH_DIR / branch / "metrics.json"

        if not metrics_file.exists():
            continue

        metrics = load_json(metrics_file)

        fitness = metrics.get("fitness",-999999)

        print("branch:",branch,"fitness:",fitness)

        if fitness > best_fitness:
            best_fitness = fitness
            best = branch

    return best,best_fitness


def promote(branch):

    main = load_json(MAIN_LEDGER)
    branch_ledger = load_json(BRANCH_DIR / branch / "ledger.json")

    fork = find_fork(main,branch_ledger)

    diff = branch_ledger[fork:]

    print("fork index:",fork)
    print("new events:",len(diff))

    if len(diff)==0:
        print("no new events")
        return

    merged = main + diff

    save_json(MAIN_LEDGER,merged)

    promoted = load_json(PROMOTED_LOG)
    promoted.append(branch)
    save_json(PROMOTED_LOG,promoted)

    print("PROMOTED:",branch)
    print("ledger size:",len(merged))


def main():

    branch,fitness = find_best_branch()

    if branch is None:
        print("no promotable branch")
        return

    print("best branch:",branch)
    print("fitness:",fitness)

    if fitness < PROMOTION_THRESHOLD:
        print("PROMOTION BLOCKED")
        return

    promote(branch)

if __name__=="__main__":
    main()
