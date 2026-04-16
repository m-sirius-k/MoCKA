import os
import csv

CSV_PATH = "runtime/record/active_log.csv"

def regenerate_csv_utf8_sig():
    if not os.path.exists(CSV_PATH):
        return "csv_not_found"

    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))

    with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    return "csv_rewritten_utf8_sig"

def execute_repair(plan_text):

    if "CSV再生成" in plan_text or "UTF-8" in plan_text:
        return regenerate_csv_utf8_sig()

    return "no_action"
