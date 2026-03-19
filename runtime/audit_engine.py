import json
import os
import hashlib
from datetime import datetime

FILES = [
"civilization_progress.json",
"civilization_governor.json",
"civilization_theory.json",
"civilization_philosophy.json",
"civilization_culture.json"
]

AUDIT_FILE = "civilization_audit.json"


def load_json(path):

    if os.path.exists(path):

        try:
            with open(path,"r",encoding="utf-8") as f:
                return json.load(f)

        except:
            return None

    return None


def compute_hash(data):

    raw = json.dumps(data,sort_keys=True).encode()
    return hashlib.sha256(raw).hexdigest()


def run():

    audit = {
        "civilization_audit":{
            "time":datetime.utcnow().isoformat(),
            "checks":[]
        }
    }

    for f in FILES:

        data = load_json(f)

        entry = {
            "file":f,
            "exists":data is not None,
            "hash":None
        }

        if data is not None:
            entry["hash"] = compute_hash(data)

        audit["civilization_audit"]["checks"].append(entry)

    with open(AUDIT_FILE,"w",encoding="utf-8") as fp:
        json.dump(audit,fp,indent=2)

    print("CIVILIZATION_AUDIT_UPDATED")


if __name__ == "__main__":
    run()
