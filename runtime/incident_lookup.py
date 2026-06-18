import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿# FILE: runtime\incident_lookup.py

import csv
import os

CSV_PATH = os.path.join("runtime", "index", "event_timeline.csv")

def load_incidents():
    incidents = []
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["type"] == "incident":
                incidents.append(row)
    return incidents

def find_similar(keyword):
    results = []
    for inc in load_incidents():
        if keyword in inc["title"]:
            results.append(inc)
    return results

if __name__ == "__main__":
    print(find_similar("ミス"))
