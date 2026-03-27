import json
import time
import os

BASE = r"C:\Users\sirok\MoCKA"
RUNTIME = os.path.join(BASE, "runtime")

LEDGER = os.path.join(RUNTIME, "main", "ledger.json")
STATE = os.path.join(RUNTIME, "state.json")
SNAPDIR = os.path.join(RUNTIME, "snapshots")

SNAP_INTERVAL = 5
MAX_SNAPSHOTS = 5


def load_json(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(p, d):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)


def rotate():

    files = sorted(
        [f for f in os.listdir(SNAPDIR) if f.startswith("ledger_")]
    )

    if len(files) <= MAX_SNAPSHOTS:
        return

    remove = files[:-MAX_SNAPSHOTS]

    for r in remove:
        os.remove(os.path.join(SNAPDIR, r))
        print("ROTATE REMOVE", r)


def snapshot():

    state = load_json(STATE)
    count = state["event_count"]

    if count % SNAP_INTERVAL != 0:
        print("snapshot skip")
        return

    ledger = load_json(LEDGER)

    ts = int(time.time())
    name = f"ledger_{ts}.json"

    path = os.path.join(SNAPDIR, name)

    save_json(path, ledger)

    print("SNAPSHOT CREATED", name)

    rotate()


snapshot()