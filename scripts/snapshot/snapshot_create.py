import json
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
