import json
import os

BASE_DIR = os.path.dirname(__file__)

INDEX_PATH = os.path.join(BASE_DIR,"incident_index.json")
BASELINE_PATH = os.path.join(BASE_DIR,"incident_baseline.json")

def create_baseline():

    if not os.path.exists(INDEX_PATH):
        print("NO_INDEX")
        return

    with open(INDEX_PATH,"r",encoding="utf-8") as f:
        index = json.load(f)

    baseline = {}

    for hid,data in index.items():

        baseline[hid] = {
            "title": data["title"]
        }

    with open(BASELINE_PATH,"w",encoding="utf-8") as f:
        json.dump(baseline,f,indent=2)

    print("INCIDENT_BASELINE_CREATED")

if __name__ == "__main__":
    create_baseline()
