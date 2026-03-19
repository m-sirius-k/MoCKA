import json
import os

BASE_DIR = os.path.dirname(__file__)

LEDGER_PATH = os.path.join(BASE_DIR,"incident_ledger.json")
INDEX_PATH = os.path.join(BASE_DIR,"incident_index.json")

def build_index():

    if not os.path.exists(LEDGER_PATH):
        return

    with open(LEDGER_PATH,"r",encoding="utf-8") as f:
        ledger = json.load(f)

    index = {}

    for event in ledger:

        hid = event.get("incident_hash","legacy")

        if hid not in index:
            index[hid] = {
                "title": event["title"],
                "count": 0
            }

        index[hid]["count"] += event.get("repeat_count",1)

    with open(INDEX_PATH,"w",encoding="utf-8") as f:
        json.dump(index,f,indent=2)

    print("INCIDENT_INDEX_UPDATED")

if __name__ == "__main__":
    build_index()
