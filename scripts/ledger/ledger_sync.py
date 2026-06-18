import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿import json

LOCAL="runtime/main/ledger.json"
REMOTE="runtime/remote_ledger.json"

def load(p):
    with open(p,"r",encoding="utf-8") as f:
        return json.load(f)

def save(p,d):
    with open(p,"w",encoding="utf-8") as f:
        json.dump(d,f,indent=2)

def main():

    local=load(LOCAL)
    remote=load(REMOTE)

    r_hash=set([e["event_hash"] for e in remote])

    missing=[e for e in local if e["event_hash"] not in r_hash]

    if not missing:
        print("REMOTE ALREADY SYNCED")
        return

    remote.extend(missing)

    save(REMOTE,remote)

    print("SYNCED EVENTS",len(missing))

if __name__=="__main__":
    main()
