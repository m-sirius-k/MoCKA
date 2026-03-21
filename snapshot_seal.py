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
        data = json.load(f)

    if isinstance(data,list):
        return {}

    return data


def save_registry(reg):

    with open(REGISTRY,"w",encoding="utf-8") as f:
        json.dump(reg,f,indent=2)


while True:

    registry = load_registry()

    if os.path.exists(SNAP_DIR):

        for f in os.listdir(SNAP_DIR):

            path = os.path.join(SNAP_DIR,f)

            if f not in registry:

                h = sha256_file(path)

                registry[f] = {
                    "sha256":h,
                    "sealed_at":int(time.time())
                }

                print("SEALED",f)

    save_registry(registry)

    time.sleep(30)

