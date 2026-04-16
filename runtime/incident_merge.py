# FILE: runtime\incident_merge.py

import csv
import os
from semantic_engine import is_similar

CSV_PATH = os.path.join("runtime", "index", "event_timeline.csv")

def load_incidents():
    data = []
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["type"] == "incident":
                data.append(row)
    return data

def find_similar(title):
    results = []
    for inc in load_incidents():
        if is_similar(title, inc["title"]):
            results.append(inc)
    return results


if __name__ == "__main__":
    res = find_similar("実行方法ミス")
    print(res)
