import json
import os

DSL_PATH = "runtime/dsl.json"

def load_dsl():
    if not os.path.exists(DSL_PATH):
        return []
    try:
        with open(DSL_PATH, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
            if not isinstance(data, list):
                return []
            return data
    except:
        print("DSL BROKEN → AUTO RESET")
        return []

def save_dsl(data):
    with open(DSL_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
