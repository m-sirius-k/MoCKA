import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿import json
import os

REGISTRY="mocka_civilization_registry.json"

def load():

    if not os.path.exists(REGISTRY):
        return []

    with open(REGISTRY,"r",encoding="utf-8-sig") as f:
        return json.load(f)

def save(data):

    with open(REGISTRY,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)

def deduplicate(records):

    nodes={}

    for r in records:
        node=r.get("node")
        nodes[node]=r

    return list(nodes.values())

def main():

    data=load()

    cleaned=deduplicate(data)

    save(cleaned)

    print("REGISTRY_DEDUP_COMPLETE")

if __name__=="__main__":
    main()
