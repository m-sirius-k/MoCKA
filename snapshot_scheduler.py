import json
import subprocess
import time

ledger_path = "runtime/main/ledger.json"

last_snapshot_events = 0
snapshot_interval = 10

while True:

    with open(ledger_path,"r",encoding="utf-8-sig") as f:
        ledger = json.load(f)

    events = len(ledger)

    if events >= last_snapshot_events + snapshot_interval:

        subprocess.run(["python","snapshot_create.py"])

        last_snapshot_events = events

    time.sleep(10)

