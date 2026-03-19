import json
import os
from datetime import datetime

FILES = [
"civilization_status.json",
"civilization_progress.json",
"civilization_governor.json",
"civilization_theory.json",
"civilization_philosophy.json",
"civilization_registry.json",
"civilization_integrity_report.json"
]

DIAG_FILE = "civilization_diagnostics.json"


def load_json(path):

    if os.path.exists(path):

        try:
            with open(path,"r",encoding="utf-8") as f:
                return json.load(f)
        except:
            return "read_error"

    return "missing"


def run():

    diag = {
        "civilization_diagnostics":{
            "time":datetime.utcnow().isoformat(),
            "checks":[]
        }
    }

    for f in FILES:

        data = load_json(f)

        entry = {
            "file":f,
            "state":"ok"
        }

        if data == "missing":
            entry["state"] = "missing"

        if data == "read_error":
            entry["state"] = "invalid"

        diag["civilization_diagnostics"]["checks"].append(entry)

    with open(DIAG_FILE,"w",encoding="utf-8") as fp:
        json.dump(diag,fp,indent=2)

    print("CIVILIZATION_DIAGNOSTICS_COMPLETE")


if __name__ == "__main__":
    run()
