import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿import json
import time

state_path = "runtime/main/state.json"
snap_dir = "runtime/main/snapshots"

with open(state_path,"r",encoding="utf-8-sig") as f:
    state = json.load(f)

ts = int(time.time())

fname = snap_dir + "/snapshot_" + str(ts) + ".json"

with open(fname,"w",encoding="utf-8") as f:
    json.dump(state,f,indent=2)

print("SNAPSHOT CREATED",fname)
