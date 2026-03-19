import json
import os
from datetime import datetime

ACTION_FILE = "civilization_action_log.json"
FEEDBACK_FILE = "civilization_feedback.json"


def load_json(path):
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    return None


def save_json(path,data):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)


def run():

    actions = load_json(ACTION_FILE)

    feedback = {
        "civilization_feedback":{
            "time":datetime.utcnow().isoformat(),
            "last_action":None,
            "feedback":"recorded"
        }
    }

    if actions:
        last = actions.get("civilization_actions",[])
        if len(last) > 0:
            feedback["civilization_feedback"]["last_action"] = last[-1].get("action")

    save_json(FEEDBACK_FILE,feedback)

    print("CIVILIZATION_FEEDBACK_RECORDED")


if __name__ == "__main__":
    run()
