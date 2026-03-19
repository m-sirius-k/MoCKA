import json
import os

BASE_DIR = os.path.dirname(__file__)

CLASS_PATH = os.path.join(BASE_DIR,"incident_classification.json")
REPAIR_PATH = os.path.join(BASE_DIR,"repair_proposals.json")

def build_proposals():

    if not os.path.exists(CLASS_PATH):
        print("NO_CLASSIFICATION")
        return

    with open(CLASS_PATH,"r",encoding="utf-8") as f:
        classes = json.load(f)

    proposals = []

    for exc,data in classes.items():

        if exc == "ModuleNotFoundError":
            proposals.append({
                "repair_id":"R001",
                "problem":"Missing Python module",
                "proposal":"Check pip install or PYTHONPATH"
            })

        elif exc == "FileNotFoundError":
            proposals.append({
                "repair_id":"R002",
                "problem":"Missing file",
                "proposal":"Verify file path or create required file"
            })

        elif exc == "Exception":
            proposals.append({
                "repair_id":"R003",
                "problem":"Generic runtime exception",
                "proposal":"Inspect stacktrace in civilization_evolution_loop"
            })

        else:
            proposals.append({
                "repair_id":"R999",
                "problem":"Unknown error",
                "proposal":"Manual inspection required"
            })

    with open(REPAIR_PATH,"w",encoding="utf-8") as f:
        json.dump(proposals,f,indent=2)

    print("REPAIR_PROPOSALS_CREATED")

if __name__ == "__main__":
    build_proposals()
