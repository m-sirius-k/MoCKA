import json
import os

ledger_path = "runtime/main/ledger.json"
config_path = "segment_config.json"

with open(config_path,"r",encoding="utf-8-sig") as f:
    cfg = json.load(f)

size = cfg["segment_size"]

with open(ledger_path,"r",encoding="utf-8-sig") as f:
    ledger = json.load(f)

events = len(ledger)

segment_id = events // size

fname = "runtime/main/ledger_" + str(segment_id).zfill(4) + ".json"

with open(fname,"w",encoding="utf-8") as f:
    json.dump(ledger,f,indent=2)

print("SEGMENT CREATED",fname)
