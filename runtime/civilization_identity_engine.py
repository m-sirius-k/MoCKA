import json
import os
from datetime import datetime

PROGRESS_FILE = "civilization_progress.json"
THEORY_FILE = "civilization_theory.json"
PHILOSOPHY_FILE = "civilization_philosophy.json"
IDENTITY_FILE = "civilization_identity.json"


def load_json(path):
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    return None


def save_json(path,data):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)


def run():

    progress = load_json(PROGRESS_FILE)
    theory = load_json(THEORY_FILE)
    philosophy = load_json(PHILOSOPHY_FILE)

    identity = {
        "civilization_identity":{
            "stage":"self_evolving_runtime",
            "progress":None,
            "dominant_strategy":None,
            "philosophy":None
        },
        "identity_updated":datetime.utcnow().isoformat()
    }

    if progress:
        identity["civilization_identity"]["progress"] = progress.get("progress")

    if theory:
        identity["civilization_identity"]["dominant_strategy"] = theory.get("dominant_strategy")

    if philosophy:
        identity["civilization_identity"]["philosophy"] = philosophy.get("principle")

    save_json(IDENTITY_FILE,identity)

    print("CIVILIZATION_IDENTITY_UPDATED")


if __name__ == "__main__":
    run()
