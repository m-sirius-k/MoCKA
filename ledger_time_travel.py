import json
import sys

LEDGER="runtime/main/ledger.json"

if len(sys.argv)<2:
    print("usage: python ledger_time_travel.py TIMESTAMP")
    exit()

target=int(sys.argv[1])

with open(LEDGER,"r",encoding="utf-8") as f:
    d=json.load(f)

events=[]

for e in d:
    if e["timestamp"]<=target:
        events.append(e)

print("TIME TRAVEL UNTIL",target)
print("EVENTS",len(events))
