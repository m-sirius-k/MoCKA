# FILE: runtime\incident_consolidate.py

import csv
import os
import json
from semantic_engine import is_similar

BASE = os.getcwd()
CSV_PATH = os.path.join(BASE, "runtime", "index", "event_timeline.csv")

def load_all():
    rows = []
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def group_incidents(rows):
    groups = []

    for r in rows:
        if r["type"] != "incident":
            continue

        placed = False

        for g in groups:
            if is_similar(r["title"], g[0]["title"]):
                g.append(r)
                placed = True
                break

        if not placed:
            groups.append([r])

    return groups

def mark_duplicates(rows, groups):
    updated = []

    for g in groups:
        # 代表は最初
        master = g[0]["event_id"]

        for r in g:
            if r["event_id"] != master:
                r["status"] = "merged"

    return rows

def save(rows):
    with open(CSV_PATH, "w", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

def run():
    rows = load_all()
    groups = group_incidents(rows)
    rows = mark_duplicates(rows, groups)
    save(rows)

    print("MERGE COMPLETE")
    print("groups:", len(groups))

if __name__ == "__main__":
    run()
