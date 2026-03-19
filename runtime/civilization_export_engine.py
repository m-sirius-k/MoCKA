import json
import os
import shutil
from datetime import datetime

EXPORT_DIR = "civilization_export"

FILES = [
"civilization_status.json",
"civilization_meta.json",
"civilization_progress.json",
"civilization_theory.json",
"civilization_philosophy.json",
"civilization_culture.json",
"civilization_registry.json",
"civilization_integrity_report.json",
"civilization_seal.json"
]


def run():

    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)

    manifest = {
        "civilization_export":{
            "time":datetime.utcnow().isoformat(),
            "files":[]
        }
    }

    for f in FILES:

        if os.path.exists(f):

            dst = os.path.join(EXPORT_DIR,f)

            shutil.copy2(f,dst)

            manifest["civilization_export"]["files"].append({
                "file":f,
                "exported":True
            })

        else:

            manifest["civilization_export"]["files"].append({
                "file":f,
                "exported":False
            })

    with open(os.path.join(EXPORT_DIR,"export_manifest.json"),"w",encoding="utf-8") as fp:
        json.dump(manifest,fp,indent=2)

    print("CIVILIZATION_EXPORT_COMPLETE")


if __name__ == "__main__":
    run()
