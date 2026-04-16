import json
import os

ANALYTICS_FILE = "mocka_civilization_analytics.json"
GOVERNOR_FILE = "mocka_civilization_governor.json"

def load_analytics():
    if not os.path.exists(ANALYTICS_FILE):
        return None
    with open(ANALYTICS_FILE,"r") as f:
        return json.load(f)

def decide_mode(stability):

    if stability < 0.4:
        return "exploration"

    if stability < 0.7:
        return "stable_operation"

    return "optimized"

def run():

    analytics = load_analytics()

    if not analytics:
        print("NO ANALYTICS")
        return

    stability = analytics.get("civilization_stability",0)

    mode = decide_mode(stability)

    governor = {
        "mode":mode,
        "stability":stability
    }

    with open(GOVERNOR_FILE,"w") as f:
        json.dump(governor,f,indent=2)

    print("GOVERNOR_UPDATED")
    print("mode:",mode)
    print("stability:",stability)

if __name__ == "__main__":
    run()
