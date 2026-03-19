import json
import os
from datetime import datetime

MEMORY_FILE = "civilization_memory.json"
ARCHIVE_DIR = "civilization_archive"


def load_json(path):
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    return None


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def run():

    memory = load_json(MEMORY_FILE)

    if memory is None:
        print("NO_MEMORY_FOUND")
        return

    ensure_dir(ARCHIVE_DIR)

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    archive_path = os.path.join(
        ARCHIVE_DIR,
        f"civilization_snapshot_{ts}.json"
    )

    with open(archive_path,"w",encoding="utf-8") as f:
        json.dump(memory,f,indent=2)

    print("CIVILIZATION_ARCHIVE_CREATED")
    print("snapshot:", archive_path)


if __name__ == "__main__":
    run()
