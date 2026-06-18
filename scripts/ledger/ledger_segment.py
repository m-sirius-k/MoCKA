import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿import json
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
