import json
import os

DIAG_FILE = "civilization_diagnostics.json"
FITNESS_FILE = "strategy_fitness.json"
PROGRESS_FILE = "civilization_progress.json"

def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path,"r") as f:
        return json.load(f)

def compute_progress(diag,fitness):

    stability = diag.get("civilization_stability",0)
    avg_fitness = diag.get("avg_strategy_fitness",0)

    strategy_count = 0
    if fitness:
        strategy_count = len(fitness)

    progress = (stability * 0.5) + (avg_fitness * 0.3) + (min(strategy_count,10)/10 * 0.2)

    return round(progress,3)

def run():

    diag = load_json(DIAG_FILE)
    fitness = load_json(FITNESS_FILE)

    if not diag:
        print("NO_DIAGNOSTICS")
        return

    progress = compute_progress(diag,fitness)

    result = {
        "civilization_progress":progress,
        "stability":diag.get("civilization_stability",0),
        "avg_fitness":diag.get("avg_strategy_fitness",0)
    }

    with open(PROGRESS_FILE,"w") as f:
        json.dump(result,f,indent=2)

    print("CIVILIZATION_PROGRESS_UPDATED")
    print("progress:",progress)

if __name__ == "__main__":
    run()
