import json
import os
from datetime import datetime

CULTURE_FILE = "civilization_culture.json"
INSTITUTION_FILE = "civilization_institutions.json"


def load_json(path):
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    return None


def save_json(path,data):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)


def run():

    culture = load_json(CULTURE_FILE)

    if culture is None:
        print("NO_CULTURE_FOUND")
        return

    institutions = {
        "institutions":[],
        "created":datetime.utcnow().isoformat()
    }

    for entry in culture.get("civilization_culture",[]):

        inst = {
            "strategy":entry.get("strategy"),
            "rule":"prefer_successful_strategy",
            "source":"culture",
            "created":datetime.utcnow().isoformat()
        }

        institutions["institutions"].append(inst)

    save_json(INSTITUTION_FILE, institutions)

    print("CIVILIZATION_INSTITUTIONS_CREATED")
    print("institution_count:", len(institutions["institutions"]))


if __name__ == "__main__":
    run()
