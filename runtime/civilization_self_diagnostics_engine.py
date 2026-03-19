import json
import os

ANALYTICS_FILE = "mocka_civilization_analytics.json"
FITNESS_FILE = "strategy_fitness.json"
DIAG_FILE = "civilization_diagnostics.json"

def load_json(path):

    if not os.path.exists(path):
        return None

    with open(path,"r") as f:
        return json.load(f)

def compute_avg_fitness(fitness):

    if not fitness:
        return 0

    scores = []

    for rid,data in fitness.items():

        score = data.get("fitness",0)
        scores.append(score)

    if not scores:
        return 0

    return sum(scores)/len(scores)

def run():

    analytics = load_json(ANALYTICS_FILE)
    fitness = load_json(FITNESS_FILE)

    stability = 0
    attempts = 0
    success = 0
    avg_fitness = 0

    if analytics:

        stability = analytics.get("civilization_stability",0)
        attempts = analytics.get("attempts",0)
        success = analytics.get("success",0)

    avg_fitness = compute_avg_fitness(fitness)

    result = {

        "civilization_stability": stability,
        "avg_strategy_fitness": avg_fitness,
        "total_attempts": attempts,
        "total_success": success
    }

    with open(DIAG_FILE,"w") as f:
        json.dump(result,f,indent=2)

    print("CIVILIZATION_DIAGNOSTICS_UPDATED")
    print("stability:",stability)
    print("avg_fitness:",avg_fitness)

if __name__ == "__main__":
    run()
