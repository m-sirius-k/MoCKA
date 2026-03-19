import json
import os
from datetime import datetime

CULTURE_FILE = "civilization_culture.json"
INSTITUTION_FILE = "civilization_institutions.json"
ECONOMY_FILE = "civilization_economy.json"
MEMORY_FILE = "civilization_memory.json"


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
    institutions = load_json(INSTITUTION_FILE)
    economy = load_json(ECONOMY_FILE)

    memory = {
        "civilization_memory":{
            "culture":culture,
            "institutions":institutions,
            "economy":economy
        },
        "memory_created":datetime.utcnow().isoformat()
    }

    save_json(MEMORY_FILE,memory)

    print("CIVILIZATION_MEMORY_CREATED")


if __name__ == "__main__":
    run()
