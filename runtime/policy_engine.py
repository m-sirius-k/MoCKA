import json
import os

BASE_DIR = os.path.dirname(__file__)

REPAIR_PATH = os.path.join(BASE_DIR,"repair_proposals.json")
DECISION_PATH = os.path.join(BASE_DIR,"repair_decision.json")

def decide():

    if not os.path.exists(REPAIR_PATH):
        print("NO_REPAIR_PROPOSALS")
        return

    with open(REPAIR_PATH,"r",encoding="utf-8") as f:
        proposals = json.load(f)

    if not proposals:
        print("NO_PROPOSALS")
        return

    decision = {
        "selected_repair": proposals[0],
        "status": "pending_human_approval"
    }

    with open(DECISION_PATH,"w",encoding="utf-8") as f:
        json.dump(decision,f,indent=2)

    print("REPAIR_DECISION_CREATED")

if __name__ == "__main__":
    decide()
