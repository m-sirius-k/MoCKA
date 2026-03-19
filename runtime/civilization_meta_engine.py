import json
import os
from datetime import datetime

IDENTITY_FILE = "civilization_identity.json"
EVOLUTION_FILE = "civilization_evolution.json"
COUNCIL_FILE = "civilization_council.json"
META_FILE = "civilization_meta.json"


def load_json(path):
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    return None


def save_json(path,data):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)


def run():

    identity = load_json(IDENTITY_FILE)
    evolution = load_json(EVOLUTION_FILE)
    council = load_json(COUNCIL_FILE)

    meta = {
        "civilization_meta":{
            "time":datetime.utcnow().isoformat(),
            "stage":None,
            "progress":None,
            "status":None
        }
    }

    if identity:
        meta["civilization_meta"]["stage"] = identity.get("civilization_identity",{}).get("stage")
        meta["civilization_meta"]["progress"] = identity.get("civilization_identity",{}).get("progress")

    if council:
        meta["civilization_meta"]["status"] = council.get("civilization_council",{}).get("status")

    save_json(META_FILE,meta)

    print("CIVILIZATION_META_UPDATED")


if __name__ == "__main__":
    run()
