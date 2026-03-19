import json
import os

ARCHIVE_FILE = "civilization_memory_archive.json"
SELECT_FILE = "selected_repair_strategy.json"

def load_archive():

    if not os.path.exists(ARCHIVE_FILE):
        return None

    with open(ARCHIVE_FILE,"r") as f:
        return json.load(f)

def run():

    archive = load_archive()

    if not archive:
        print("NO_MEMORY_AVAILABLE")
        return

    best = None
    best_score = -1

    for rid,data in archive.items():

        score = data.get("fitness",0)

        if score > best_score:
            best_score = score
            best = rid

    result = {
        "selected_strategy":best,
        "source":"civilization_memory"
    }

    with open(SELECT_FILE,"w") as f:
        json.dump(result,f,indent=2)

    print("MEMORY_STRATEGY_SELECTED")
    print("strategy:",best)

if __name__ == "__main__":
    run()
