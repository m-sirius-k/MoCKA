import json
import os
from datetime import datetime

FILES = [
"civilization_status.json",
"civilization_progress.json",
"civilization_summary.json",
"civilization_registry.json",
"civilization_integrity_report.json",
"civilization_seal.json"
]

AUDIT_FILE = "civilization_audit_log.json"


def check(path):

    if os.path.exists(path):
        return True
    return False


def run():

    audit = {
        "civilization_audit":{
            "time":datetime.utcnow().isoformat(),
            "checks":[]
        }
    }

    for f in FILES:

        entry = {
            "file":f,
            "exists":check(f)
        }

        audit["civilization_audit"]["checks"].append(entry)

    with open(AUDIT_FILE,"w",encoding="utf-8") as fp:
        json.dump(audit,fp,indent=2)

    print("CIVILIZATION_AUDIT_COMPLETE")


if __name__ == "__main__":
    run()
