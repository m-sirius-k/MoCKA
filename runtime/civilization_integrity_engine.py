import json
import os
from datetime import datetime

INTEGRITY_FILE = "civilization_integrity_report.json"

FILES = [
"civilization_progress.json",
"civilization_governor.json",
"civilization_theory.json",
"civilization_philosophy.json",
"civilization_culture.json",
"civilization_institutions.json",
"civilization_economy.json",
"civilization_memory.json",
"civilization_archive",
"civilization_timeline.json",
"civilization_identity.json",
"civilization_signal.json"
]


def check_file(path):

    if os.path.isdir(path):
        return True

    if os.path.exists(path):

        try:
            with open(path,"r",encoding="utf-8") as f:
                json.load(f)
            return True

        except:
            return False

    return False


def run():

    report = {
        "civilization_integrity":{
            "time":datetime.utcnow().isoformat(),
            "checks":[]
        }
    }

    for f in FILES:

        result = check_file(f)

        entry = {
            "target":f,
            "ok":result
        }

        report["civilization_integrity"]["checks"].append(entry)

    with open(INTEGRITY_FILE,"w",encoding="utf-8") as fp:
        json.dump(report,fp,indent=2)

    print("CIVILIZATION_INTEGRITY_CHECK_COMPLETE")


if __name__ == "__main__":
    run()
