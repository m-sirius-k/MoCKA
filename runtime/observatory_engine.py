import json
import os
from datetime import datetime

FILES = [
"civilization_progress.json",
"civilization_governor.json",
"civilization_theory.json",
"civilization_philosophy.json",
"civilization_culture.json"
]

OUTPUT_FILE = "civilization_observatory.json"


def load_json(path):
    if os.path.exists(path):
        try:
            with open(path,"r",encoding="utf-8") as f:
                return json.load(f)
        except:
            return "invalid"
    return "missing"


def run():

    report = {
        "civilization_observatory":{
            "time":datetime.utcnow().isoformat(),
            "state":[]
        }
    }

    for f in FILES:

        data = load_json(f)

        entry = {
            "file":f,
            "status":"ok"
        }

        if data == "missing":
            entry["status"] = "missing"

        if data == "invalid":
            entry["status"] = "invalid"

        report["civilization_observatory"]["state"].append(entry)

    with open(OUTPUT_FILE,"w",encoding="utf-8") as fp:
        json.dump(report,fp,indent=2)

    print("CIVILIZATION_OBSERVATORY_UPDATED")


if __name__ == "__main__":
    run()
