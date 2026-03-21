import json
import os
import time

LEDGER = "runtime/main/ledger.json"
STATE  = "runtime/state.json"

def load_ledger():

    if not os.path.exists(LEDGER):
        return []

    with open(LEDGER,"r",encoding="utf-8-sig") as f:
        return json.load(f)

def apply_events(events):

    state = {
        "event_count":0,
        "last_event":None
    }

    for e in events:
        state["event_count"] += 1
        state["last_event"] = e

    return state

print("STATE ENGINE START")

while True:

    events = load_ledger()

    state = apply_events(events)

    with open(STATE,"w",encoding="utf-8") as f:
        json.dump(state,f,indent=2)

    print("STATE UPDATED",state["event_count"])

    time.sleep(5)

