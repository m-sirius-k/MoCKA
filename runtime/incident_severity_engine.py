import json
import os

LEDGER_FILE = "incident_ledger.json"
ALERT_FILE = "incident_severity_alert.json"

THRESHOLD = 50

def load_ledger():
    if not os.path.exists(LEDGER_FILE):
        return None
    with open(LEDGER_FILE,"r") as f:
        return json.load(f)

def run():

    ledger = load_ledger()

    if not ledger:
        print("LEDGER_NOT_FOUND")
        return

    alerts = []

    for inc in ledger:

        count = inc.get("count",0)

        if count >= THRESHOLD:
            alerts.append({
                "incident":inc.get("hash"),
                "count":count,
                "severity":"high"
            })

    with open(ALERT_FILE,"w") as f:
        json.dump(alerts,f,indent=2)

    print("SEVERITY_SCAN_COMPLETE")
    print("alerts:",len(alerts))

if __name__ == "__main__":
    run()
