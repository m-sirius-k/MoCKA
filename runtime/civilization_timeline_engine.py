import json
import os
from datetime import datetime

TIMELINE_FILE = "civilization_timeline.json"
THEORY_FILE = "civilization_theory.json"
PHILOSOPHY_FILE = "civilization_philosophy.json"


def load_json(path):
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    return None


def save_json(path,data):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)


def run():

    theory = load_json(THEORY_FILE)
    philosophy = load_json(PHILOSOPHY_FILE)
    timeline = load_json(TIMELINE_FILE)

    if timeline is None:
        timeline = {
            "civilization_timeline":[]
        }

    event = {
        "timestamp":datetime.utcnow().isoformat(),
        "dominant_strategy": None,
        "philosophy": None
    }

    if theory:
        event["dominant_strategy"] = theory.get("dominant_strategy")

    if philosophy:
        event["philosophy"] = philosophy.get("principle")

    timeline["civilization_timeline"].append(event)

    save_json(TIMELINE_FILE,timeline)

    print("CIVILIZATION_TIMELINE_UPDATED")
    print("events:",len(timeline["civilization_timeline"]))


if __name__ == "__main__":
    run()
