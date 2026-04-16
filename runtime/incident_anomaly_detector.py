import json
import os

BASE_DIR = os.path.dirname(__file__)

INDEX_PATH = os.path.join(BASE_DIR,"incident_index.json")
BASELINE_PATH = os.path.join(BASE_DIR,"incident_baseline.json")

def detect_new_incidents():

    if not os.path.exists(BASELINE_PATH):
        print("NO_BASELINE")
        return

    with open(INDEX_PATH,"r",encoding="utf-8") as f:
        index = json.load(f)

    with open(BASELINE_PATH,"r",encoding="utf-8") as f:
        baseline = json.load(f)

    new_incidents = []

    for hid,data in index.items():

        if hid not in baseline:

            new_incidents.append({
                "incident_hash": hid,
                "title": data["title"],
                "count": data["count"]
            })

    if new_incidents:

        print("NEW_INCIDENT_DETECTED")
        print(json.dumps(new_incidents,indent=2))

    else:

        print("NO_NEW_INCIDENT")

if __name__ == "__main__":
    detect_new_incidents()
