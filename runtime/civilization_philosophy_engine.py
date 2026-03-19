import json
import os
import time

THEORY_FILE = "civilization_theory.json"
PHIL_FILE = "civilization_philosophy.json"

def load_theory():
    if not os.path.exists(THEORY_FILE):
        return None
    with open(THEORY_FILE,"r") as f:
        return json.load(f)

def run():

    theory = load_theory()

    if not theory:
        print("NO_THEORY")
        return

    dominant = theory.get("dominant_strategy")
    confidence = theory.get("confidence",0)

    if confidence > 0.6:
        principle = "exploit_successful_strategy"
    elif confidence > 0.3:
        principle = "balanced_explore_exploit"
    else:
        principle = "strong_exploration"

    philosophy = {
        "timestamp":int(time.time()),
        "dominant_strategy":dominant,
        "confidence":confidence,
        "civilization_principle":principle
    }

    with open(PHIL_FILE,"w") as f:
        json.dump(philosophy,f,indent=2)

    print("CIVILIZATION_PHILOSOPHY_UPDATED")
    print("principle:",principle)

if __name__ == "__main__":
    run()
