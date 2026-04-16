import os
import csv

CSV_PATH = "runtime/record/active_log.csv"

def validate_csv_utf8():
    if not os.path.exists(CSV_PATH):
        return {"valid": False, "reason": "file_missing"}

    try:
        with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
            list(csv.reader(f))
        return {"valid": True}
    except:
        return {"valid": False, "reason": "encoding_error"}

def validate_repair(exec_result):

    if exec_result == "csv_rewritten_utf8_sig":
        return validate_csv_utf8()

    return {"valid": True}
