import json
import os
from datetime import datetime

LEARNING_FILE = "civilization_learning_log.json"
PROGRESS_FILE = "civilization_progress.json"
EVOLUTION_FILE = "civilization_evolution.json"


def load_json(path):
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    return None


def save_json(path,data):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)


def run():

    learning = load_json(LEARNING_FILE)
    progress = load_json(PROGRESS_FILE)

    current_progress = 0.0

    if progress:
        current_progress = progress.get("progress",0.0)

    learning_events = 0

    if learning:
        learning_events = len(learning.get("civilization_learning",[]))

    evolution = {
        "civilization_evolution":{
            "time":datetime.utcnow().isoformat(),
            "learning_events":learning_events,
            "progress":current_progress
        }
    }

    save_json(EVOLUTION_FILE,evolution)

    print("CIVILIZATION_EVOLUTION_UPDATED")


if __name__ == "__main__":
    run()
