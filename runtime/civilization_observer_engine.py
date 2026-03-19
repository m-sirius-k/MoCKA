import json
import os
from datetime import datetime

SIGNAL_FILE = "civilization_signal.json"
TIMELINE_FILE = "civilization_timeline.json"
PROGRESS_FILE = "civilization_progress.json"
OBSERVER_FILE = "civilization_observer.json"


def load_json(path):
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    return None


def save_json(path,data):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)


def run():

    signal = load_json(SIGNAL_FILE)
    timeline = load_json(TIMELINE_FILE)
    progress = load_json(PROGRESS_FILE)

    observer = {
        "observer_snapshot":{
            "time":datetime.utcnow().isoformat(),
            "signal_status":None,
            "timeline_events":0,
            "progress":None
        }
    }

    if signal:
        observer["observer_snapshot"]["signal_status"] = signal.get("civilization_signal",{}).get("status")

    if timeline:
        observer["observer_snapshot"]["timeline_events"] = len(timeline.get("civilization_timeline",[]))

    if progress:
        observer["observer_snapshot"]["progress"] = progress.get("progress")

    save_json(OBSERVER_FILE,observer)

    print("CIVILIZATION_OBSERVER_UPDATED")


if __name__ == "__main__":
    run()
