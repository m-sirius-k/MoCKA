import json
import sys

LEDGER="runtime/main/ledger.json"

if len(sys.argv)<2:
    print("usage: python ledger_replay.py EVENT_ID")
    exit()

target=int(sys.argv[1])

with open(LEDGER,"r",encoding="utf-8") as f:
    d=json.load(f)

state={
    "events":0
}

for e in d:

    if e["event_id"]>target:
        break

    state["events"]+=1

print("REPLAY UNTIL EVENT",target)
print("STATE",state)
