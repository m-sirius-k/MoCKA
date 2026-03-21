# FILE: runtime\policy_engine.py

import csv
import os

CSV_PATH = os.path.join("runtime", "index", "event_timeline.csv")

def load_active_incidents():
    data = []
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["type"] == "incident" and row["status"] == "active":
                data.append(row)
    return data

def decide(action_name):
    incidents = load_active_incidents()

    if incidents:
        print("POLICY: CAUTION (incident exists)")
        return "caution"

    return "normal"

if __name__ == "__main__":
    print(decide("test"))
