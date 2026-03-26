import json
import os

DSL_PATH = "runtime/dsl.json"

def load_json(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except:
        print("DSL BROKEN → RESET")
        return []

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def main():
    dsl = load_json(DSL_PATH)

    if not isinstance(dsl, list):
        dsl = []

    # ダミー生成（最低限）
    if len(dsl) < 3:
        dsl.append({"id": "seed_" + str(len(dsl)), "action": "EXPLORE"})

    save_json(DSL_PATH, dsl)

    print("CROSS CONTEXT GENERATED:", dsl[-1]["id"])

if __name__ == "__main__":
    main()
