import json
import os
from datetime import datetime

PROGRESS_FILE = "civilization_progress.json"
GOVERNOR_FILE = "civilization_governor.json"
GUARDIAN_FILE = "civilization_guardian.json"


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
    governor = load_json(GOVERNOR_FILE)

    stability = None
    mode = None

    if governor:
        stability = governor.get("stability")
        mode = governor.get("mode")

    guardian = {
        "guardian_check":{
            "time":datetime.utcnow().isoformat(),
            "mode":mode,
            "stability":stability,
            "alert":False
        }
    }

    if stability is not None:
        if stability < 0.20:
            guardian["guardian_check"]["alert"] = True

    save_json(GUARDIAN_FILE,guardian)

    print("CIVILIZATION_GUARDIAN_CHECK_COMPLETE")


if __name__ == "__main__":
    run()
