import json
import os
from datetime import datetime

FEEDBACK_FILE = "civilization_feedback.json"
LEARNING_FILE = "civilization_learning_log.json"


def load_json(path):
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    return None


def save_json(path,data):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)


def run():

    feedback = load_json(FEEDBACK_FILE)

    learning = {
        "civilization_learning":[]
    }

    if feedback:

        entry = {
            "time":datetime.utcnow().isoformat(),
            "observed_action":feedback.get("civilization_feedback",{}).get("last_action"),
            "learning_state":"recorded"
        }

        learning["civilization_learning"].append(entry)

    save_json(LEARNING_FILE,learning)

    print("CIVILIZATION_LEARNING_UPDATED")


if __name__ == "__main__":
    run()
