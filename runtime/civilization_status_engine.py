import json
import os
from datetime import datetime

PROGRESS_FILE = "civilization_progress.json"
GOVERNOR_FILE = "civilization_governor.json"
THEORY_FILE = "civilization_theory.json"
PHILOSOPHY_FILE = "civilization_philosophy.json"

STATUS_FILE = "civilization_status.json"


def load_json(path):
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    return None


def run():

    progress = load_json(PROGRESS_FILE)
    governor = load_json(GOVERNOR_FILE)
    theory = load_json(THEORY_FILE)
    philosophy = load_json(PHILOSOPHY_FILE)

    status = {
        "civilization_status":{
            "time":datetime.utcnow().isoformat(),
            "mode":None,
            "stability":None,
            "progress":None,
            "dominant_strategy":None,
            "philosophy":None
        }
    }

    if governor:
        status["civilization_status"]["mode"] = governor.get("mode")
        status["civilization_status"]["stability"] = governor.get("stability")

    if progress:
        status["civilization_status"]["progress"] = progress.get("progress")

    if theory:
        status["civilization_status"]["dominant_strategy"] = theory.get("dominant_strategy")

    if philosophy:
        status["civilization_status"]["philosophy"] = philosophy.get("principle")

    with open(STATUS_FILE,"w",encoding="utf-8") as f:
        json.dump(status,f,indent=2)

    print("CIVILIZATION_STATUS_UPDATED")


if __name__ == "__main__":
    run()
