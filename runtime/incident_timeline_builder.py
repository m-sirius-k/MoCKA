import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)

LEDGER_PATH = os.path.join(BASE_DIR,"incident_ledger.json")
TIMELINE_PATH = os.path.join(BASE_DIR,"incident_timeline.json")

def build_timeline():

    if not os.path.exists(LEDGER_PATH):
        print("NO_LEDGER")
        return

    with open(LEDGER_PATH,"r",encoding="utf-8") as f:
        ledger = json.load(f)

    timeline = {}

    for event in ledger:

        ts = event.get("first_seen",event.get("timestamp"))
        dt = datetime.utcfromtimestamp(ts)

        key = dt.strftime("%Y-%m-%d %H")

        if key not in timeline:
            timeline[key] = 0

        timeline[key] += event.get("repeat_count",1)

    with open(TIMELINE_PATH,"w",encoding="utf-8") as f:
        json.dump(timeline,f,indent=2)

    print("INCIDENT_TIMELINE_UPDATED")

if __name__ == "__main__":
    build_timeline()
