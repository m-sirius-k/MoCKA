import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿import json
import os

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

    try:
        remote=load(REMOTE)
    except:
        print("REMOTE NOT FOUND")
        return

    if len(remote)>len(local):

        save(LOCAL,remote)

        print("REMOTE LEDGER ADOPTED")

    elif len(local)>len(remote):

        save(REMOTE,local)

        print("LOCAL LEDGER DOMINANT")

    else:

        print("LEDGER EQUAL")

if __name__=="__main__":
    main()
