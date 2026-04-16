import os
import time
import json
import shutil
from datetime import datetime

BASE = r"C:\Users\sirok\MoCKA\network"

NODE_NAME = "node1"
OUTBOX = os.path.join(BASE, "node1_out")
INBOX  = os.path.join(BASE, "node2_out")

INPUT_PATH = "input.json"

def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def send_message():
    if not os.path.exists(INPUT_PATH):
        return

    data = load_json(INPUT_PATH)
    if not data:
        return

    fname = datetime.utcnow().timestamp()
    path = os.path.join(OUTBOX, f"{fname}.json")

    save_json(path, data)
    save_json(INPUT_PATH, [])

    print("SENT:", path)

def receive_message():
    files = os.listdir(INBOX)

    for f in files:
        full = os.path.join(INBOX, f)

        try:
            data = load_json(full)

            if os.path.exists(INPUT_PATH):
                current = load_json(INPUT_PATH)
            else:
                current = []

            current.extend(data)
            save_json(INPUT_PATH, current)

            os.remove(full)

            print("RECEIVED:", f)

        except:
            continue

def main():
    print("=== NODE BRIDGE START ===")

    while True:
        send_message()
        receive_message()
        time.sleep(3)

if __name__ == "__main__":
    main()
