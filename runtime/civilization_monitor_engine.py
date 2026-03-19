import json
import os
from datetime import datetime

MONITOR_FILE = "civilization_monitor.json"

FILES_TO_CHECK = [
"civilization_progress.json",
"civilization_theory.json",
"civilization_philosophy.json",
"civilization_culture.json",
"civilization_institutions.json",
"civilization_economy.json",
"civilization_memory.json",
"civilization_timeline.json",
"civilization_identity.json",
"civilization_signal.json"
]


def run():

    report = {
        "civilization_monitor":{
            "time":datetime.utcnow().isoformat(),
            "files":[]
        }
    }

    for f in FILES_TO_CHECK:

        entry = {
            "file":f,
            "exists":os.path.exists(f)
        }

        report["civilization_monitor"]["files"].append(entry)

    with open(MONITOR_FILE,"w",encoding="utf-8") as fp:
        json.dump(report,fp,indent=2)

    print("CIVILIZATION_MONITOR_UPDATED")


if __name__ == "__main__":
    run()
