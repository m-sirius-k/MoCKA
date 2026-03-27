import os
import json
import hashlib
import time

SNAP_DIR = "runtime/snapshots"
REGISTRY = "runtime/seal_registry.json"

def sha256_file(path):

    with open(path,"rb") as f:
        data = f.read()

    return hashlib.sha256(data).hexdigest()

def load_registry():

    if not os.path.exists(REGISTRY):
        return {}

    with open(REGISTRY,"r",encoding="utf-8-sig") as f:
        return json.load(f)

while True:

    registry = load_registry()

    for f in registry:

        path = os.path.join(SNAP_DIR,f)

        if not os.path.exists(path):

            print("SNAPSHOT MISSING",f)
            continue

        h = sha256_file(path)

        if h != registry[f]["sha256"]:

            print("TAMPER DETECTED",f)

        else:

            print("VERIFIED",f)

    time.sleep(30)

