import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿import json
import os
import shutil

MODEL_FILE = "repair_strategy_model.json"
MEMORY_FILE = "civilization_memory_archive.json"

NETWORK_DIR = "civilization_network"


def ensure_network():

    if not os.path.exists(NETWORK_DIR):
        os.makedirs(NETWORK_DIR)


def broadcast(file):

    target = os.path.join(NETWORK_DIR, os.path.basename(file))

    if os.path.exists(file):
        shutil.copy(file,target)
        print("BROADCAST:",file)


def run():

    ensure_network()

    broadcast(MODEL_FILE)
    broadcast(MEMORY_FILE)

    print("CIVILIZATION_SYNC_COMPLETE")


if __name__ == "__main__":
    run()
