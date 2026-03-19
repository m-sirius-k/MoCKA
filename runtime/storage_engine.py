import json
import os
import shutil
from datetime import datetime

SOURCE_FILES = [
"civilization_progress.json",
"civilization_governor.json",
"civilization_theory.json",
"civilization_philosophy.json",
"civilization_culture.json"
]

STORAGE_DIR = "civilization_storage"
SNAPSHOT_DIR = "civilization_storage\\snapshots"
EXPORT_DIR = "civilization_storage\\export"


def ensure_dirs():

    for d in [STORAGE_DIR, SNAPSHOT_DIR, EXPORT_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)


def load_json(path):

    if os.path.exists(path):

        try:
            with open(path,"r",encoding="utf-8") as f:
                return json.load(f)

        except:
            return None

    return None


def run():

    ensure_dirs()

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    snapshot = {
        "civilization_snapshot":{
            "time":timestamp,
            "data":{}
        }
    }

    for f in SOURCE_FILES:

        data = load_json(f)

        snapshot["civilization_snapshot"]["data"][f] = data

        if os.path.exists(f):

            shutil.copy2(
                f,
                os.path.join(EXPORT_DIR,f)
            )

    snap_file = os.path.join(
        SNAPSHOT_DIR,
        "snapshot_" + timestamp + ".json"
    )

    with open(snap_file,"w",encoding="utf-8") as fp:
        json.dump(snapshot,fp,indent=2)

    print("CIVILIZATION_STORAGE_UPDATED")


if __name__ == "__main__":
    run()
