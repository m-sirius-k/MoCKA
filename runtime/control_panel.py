import json
import os
import time

INPUT_PATH = "input.json"

def load_intent():
    if not os.path.exists(INPUT_PATH):
        return None
    try:
        with open(INPUT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("intent")
    except:
        return None

while True:
    os.system("cls")

    print("=== MoCKA CONTROL PANEL ===")

    intent = load_intent()

    if intent:
        print("")
        print("[INTENT]")
        print("id:", intent.get("intent_id"))
        print("type:", intent.get("type"))
        print("goal:", intent.get("goal"))
        print("source:", intent.get("source"))
    else:
        print("")
        print("[INTENT] NONE")

    time.sleep(1)
