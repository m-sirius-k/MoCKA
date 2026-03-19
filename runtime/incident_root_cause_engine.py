import json
import os

LEDGER_FILE = "incident_ledger.json"
ROOT_CAUSE_FILE = "incident_root_cause_queue.json"

THRESHOLD = 60

def load_ledger():

    if not os.path.exists(LEDGER_FILE):
        return []

    with open(LEDGER_FILE,"r") as f:
        return json.load(f)

def run():

    ledger = load_ledger()

    queue = []

    for item in ledger:

        count = item.get("count",0)

        if count >= THRESHOLD:

            queue.append({
                "incident":item.get("hash"),
                "count":count,
                "analysis_required":True
            })

    with open(ROOT_CAUSE_FILE,"w") as f:
        json.dump(queue,f,indent=2)

    print("ROOT_CAUSE_SCAN_COMPLETE")
    print("items:",len(queue))

if __name__ == "__main__":
    run()
