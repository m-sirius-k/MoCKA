import os
from datetime import datetime

LOG_PATH = r"C:\Users\sirok\MoCKA\data\events.csv"

def parse_log():
    if not os.path.exists(LOG_PATH):
        print("LOG NOT FOUND")
        return []

    with open(LOG_PATH, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()

    return lines[1:]

def extract_drift(events):
    drift_history = []
    for e in events:
        if "caliber_b" in e and "drift=" in e:
            try:
                drift_part = e.split("drift=")[1]
                drift_value = float(drift_part.split(":")[0])
                drift_history.append(drift_value)
            except:
                continue
    return drift_history

def summary(events):
    total = len(events)
    errors = sum(1 for e in events if "error" in e.lower())
    actions = sum(1 for e in events if "playwright" in e.lower())
    routes = sum(1 for e in events if "router" in e.lower())

    return total, errors, actions, routes

def main():
    events = parse_log()
    drift = extract_drift(events)
    total, errors, actions, routes = summary(events)

    print("=== MoCKA Dashboard ===")
    print("Time:", datetime.now().isoformat())
    print("------------------------")
    print("Total Events:", total)
    print("Errors:", errors)
    print("Router Decisions:", routes)
    print("Physical Actions:", actions)
    print("------------------------")
    print("Drift History:", drift)
    if drift:
        print("Current Drift:", drift[-1])
    print("------------------------")

if __name__ == "__main__":
    main()

