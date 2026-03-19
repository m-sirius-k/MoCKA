import json
import os
from datetime import datetime

OBSERVER_FILE = "civilization_observer.json"
GUARDIAN_FILE = "civilization_guardian.json"
THEORY_FILE = "civilization_theory.json"
COUNCIL_FILE = "civilization_council.json"


def load_json(path):
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    return None


def save_json(path,data):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)


def run():

    observer = load_json(OBSERVER_FILE)
    guardian = load_json(GUARDIAN_FILE)
    theory = load_json(THEORY_FILE)

    council = {
        "civilization_council":{
            "time":datetime.utcnow().isoformat(),
            "status":"stable",
            "dominant_strategy":None,
            "alerts":False
        }
    }

    if theory:
        council["civilization_council"]["dominant_strategy"] = theory.get("dominant_strategy")

    if guardian:
        alert = guardian.get("guardian_check",{}).get("alert")
        council["civilization_council"]["alerts"] = alert
        if alert:
            council["civilization_council"]["status"] = "warning"

    save_json(COUNCIL_FILE,council)

    print("CIVILIZATION_COUNCIL_UPDATED")


if __name__ == "__main__":
    run()
