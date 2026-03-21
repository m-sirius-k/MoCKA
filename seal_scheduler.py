import json
import subprocess
import time

ledger_path = "runtime/main/ledger.json"

last_events = 0

while True:

    with open(ledger_path,"r") as f:
        ledger = json.load(f)

    events = len(ledger)

    if events > last_events:

        subprocess.run(["python","seal_commit.py"])

        last_events = events

    time.sleep(10)

