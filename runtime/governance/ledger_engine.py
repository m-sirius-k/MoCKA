import csv
import hashlib
import os
import json

CSV_PATH = "runtime/record/event_log.csv"
LEDGER_PATH = "runtime/record/ledger.json"

def hash_row(row, prev_hash):
    data = prev_hash + json.dumps(row, ensure_ascii=False)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def build_ledger():
    if not os.path.exists(CSV_PATH):
        return []

    ledger = []
    prev_hash = "GENESIS"

    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            h = hash_row(row, prev_hash)

            ledger.append({
                "event_id": row["event_id"],
                "hash": h,
                "prev_hash": prev_hash
            })

            prev_hash = h

    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(ledger, f, ensure_ascii=False, indent=2)

    return ledger

def verify_ledger():
    if not os.path.exists(LEDGER_PATH):
        return False

    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        ledger = json.load(f)

    prev_hash = "GENESIS"

    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = list(csv.DictReader(f))

    for i, entry in enumerate(ledger):
        expected = hash_row(reader[i], prev_hash)

        if entry["hash"] != expected:
            return {
                "valid": False,
                "error_index": i
            }

        prev_hash = entry["hash"]

    return {
        "valid": True,
        "total_events": len(ledger)
    }

if __name__ == "__main__":
    print("=== BUILD LEDGER ===")
    build_ledger()

    print("=== VERIFY LEDGER ===")
    result = verify_ledger()
    print("RESULT:", result)
