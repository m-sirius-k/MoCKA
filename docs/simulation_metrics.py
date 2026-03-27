import json
import os

BASE_DIR = r"C:\Users\sirok\MoCKA"
BRANCH_DIR = os.path.join(BASE_DIR,"runtime","branches")

def load(path):
    with open(path,"r",encoding="utf-8") as f:
        return json.load(f)

print("=== MoCKA Simulation Metrics ===")

branch = input("branch id: ")

ledger_path = os.path.join(BRANCH_DIR,branch,"ledger.json")

if not os.path.exists(ledger_path):
    print("branch not found")
    exit()

ledger = load(ledger_path)

failures = 0
recoveries = 0
heartbeats = 0

for e in ledger:

    t = e["type"]

    if "failure" in t:
        failures += 1

    if "recovery" in t:
        recoveries += 1

    if "heartbeat" in t:
        heartbeats += 1

print("")
print("event count:",len(ledger))
print("failures:",failures)
print("recoveries:",recoveries)
print("heartbeats:",heartbeats)

score = recoveries - failures

print("")
print("stability score:",score)

if score >= 0:
    print("system outcome: STABLE")
else:
    print("system outcome: UNSTABLE")
