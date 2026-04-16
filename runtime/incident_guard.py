# FILE: runtime\incident_guard.py

import csv
import os
import sys
import json
import subprocess

CSV_PATH = os.path.join("runtime", "index", "event_timeline.csv")
BASE = os.getcwd()

def load_incidents():
    incidents = []
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["type"] == "incident":
                incidents.append(row)
    return incidents

def load_detail(path):
    full = os.path.join(BASE, path)
    if os.path.exists(full):
        with open(full, encoding="utf-8") as f:
            return json.load(f)
    return None

def check(keyword):
    for inc in load_incidents():
        if keyword in inc["title"]:
            return inc
    return None

def guard(keyword):
    hit = check(keyword)

    if hit:
        print("=== INCIDENT DETECTED ===")
        print(hit)

        detail = load_detail(hit["storage_path"])
        if detail:
            print("\n=== INCIDENT DETAIL ===")
            print(json.dumps(detail["content"], ensure_ascii=False, indent=2))

            if isinstance(detail["content"], dict) and "fix" in detail["content"]:
                fix = detail["content"]["fix"]

                print("\n=== AUTO FIX SUGGESTION ===")
                print(fix)

                # 自動実行
                subprocess.run(["python", "runtime/incident_auto_executor.py", fix])

        print("\nACTION CONTROLLED")
        sys.exit(1)

    else:
        print("SAFE")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python incident_guard.py <keyword>")
        sys.exit(0)

    guard(sys.argv[1])
