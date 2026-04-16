import json
import time
import os

LEDGER_PATH = "ledger.json"
KNOWLEDGE_PATH = "knowledge_log.json"

def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def normalize(text):
    return str(text).lower().strip()

def to_int(x):
    try:
        return int(x)
    except:
        return 0

def main():
    print("=== KNOWLEDGE BUILDER FIXED ===")

    while True:
        if not os.path.exists(LEDGER_PATH):
            time.sleep(5)
            continue

        ledger = load_json(LEDGER_PATH)

        if not os.path.exists(KNOWLEDGE_PATH):
            save_json(KNOWLEDGE_PATH, {})

        knowledge = load_json(KNOWLEDGE_PATH)

        updated = False

        for entry in ledger:
            if entry.get("event_type") != "external_input":
                continue

            key = normalize(entry.get("message",""))

            if key not in knowledge:
                knowledge[key] = {
                    "count": 0,
                    "score_total": 0
                }

            score = to_int(entry.get("score", 0))

            knowledge[key]["count"] += 1
            knowledge[key]["score_total"] += score

            updated = True

        if updated:
            save_json(KNOWLEDGE_PATH, knowledge)
            print("KNOWLEDGE UPDATED:", len(knowledge))

        time.sleep(5)

if __name__ == "__main__":
    main()
