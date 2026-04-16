import json
import os

EVENT_PATH = "runtime/events.json"
SYS_PATH = "runtime/system_state.json"

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def main():
    events = load_json(EVENT_PATH, {"events":[]})["events"]

    error = 0
    load = 1

    for e in events:
        if e.get("type") == "ERROR":
            error += 1
        if e.get("type") == "LOAD":
            load += e.get("value", 1)

    state = {
        "system_state": {
            "error_level": error,
            "load": load
        }
    }

    save_json(SYS_PATH, state)

    print("STATE UPDATED FROM EVENTS", state)

if __name__ == "__main__":
    main()
