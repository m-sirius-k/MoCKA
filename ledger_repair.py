import json
import os

BASE = r"C:\Users\sirok\MoCKA"

LEDGER = os.path.join(BASE, "runtime", "main", "ledger.json")
SNAPDIR = os.path.join(BASE, "runtime", "snapshots")

def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def latest_snapshot():
    snaps = [f for f in os.listdir(SNAPDIR) if f.startswith("ledger_")]
    if not snaps:
        print("NO SNAPSHOT")
        return None
    snaps.sort()
    return os.path.join(SNAPDIR, snaps[-1])

snap = latest_snapshot()

if snap is None:
    exit()

print("RESTORE FROM SNAPSHOT", snap)

data = load(snap)

save(LEDGER, data)

print("LEDGER RESTORED")
