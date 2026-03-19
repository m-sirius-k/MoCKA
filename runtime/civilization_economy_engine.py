import json
import os
from datetime import datetime

INSTITUTION_FILE = "civilization_institutions.json"
ECONOMY_FILE = "civilization_economy.json"


def load_json(path):
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    return None


def save_json(path,data):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)


def run():

    institutions = load_json(INSTITUTION_FILE)

    economy = {
        "economic_priority":[],
        "created":datetime.utcnow().isoformat()
    }

    if institutions:
        for inst in institutions.get("institutions",[]):

            entry = {
                "strategy":inst.get("strategy"),
                "priority":1.0,
                "allocation":"repair_focus",
                "timestamp":datetime.utcnow().isoformat()
            }

            economy["economic_priority"].append(entry)

    save_json(ECONOMY_FILE,economy)

    print("CIVILIZATION_ECONOMY_CREATED")
    print("economic_entries:",len(economy["economic_priority"]))


if __name__ == "__main__":
    run()
