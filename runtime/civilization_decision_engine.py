import json
import os
from datetime import datetime

COUNCIL_FILE = "civilization_council.json"
DECISION_FILE = "civilization_decision.json"


def load_json(path):
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    return None


def save_json(path,data):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)


def run():

    council = load_json(COUNCIL_FILE)

    decision = {
        "civilization_decision":{
            "time":datetime.utcnow().isoformat(),
            "action":"explore",
            "reason":"default_exploration"
        }
    }

    if council:
        status = council.get("civilization_council",{}).get("status")

        if status == "warning":
            decision["civilization_decision"]["action"] = "stabilize"
            decision["civilization_decision"]["reason"] = "guardian_alert"

    save_json(DECISION_FILE,decision)

    print("CIVILIZATION_DECISION_CREATED")


if __name__ == "__main__":
    run()
