import os
import sys
import json
from datetime import datetime

sys.path.append(os.path.abspath("."))

from runtime.record.csv_record_engine import record_event

BASE_PATH = "docs"

def validate_fields(what, why, how, countermeasure, recurrence_condition):
    fields = [what, why, how, countermeasure, recurrence_condition]
    if any(f is None or str(f).strip() == "" for f in fields):
        raise ValueError("5W1H fields must not be empty")

def generate_id(prefix):
    return f"{prefix}_{int(datetime.utcnow().timestamp())}"

def save_incident(what, why, how, countermeasure, recurrence_condition):
    validate_fields(what, why, how, countermeasure, recurrence_condition)

    incident_id = generate_id("INC")

    data = {
        "id": incident_id,
        "timestamp": datetime.utcnow().isoformat(),
        "What": what,
        "Why": why,
        "How": how,
        "Countermeasure": countermeasure,
        "RecurrenceCondition": recurrence_condition
    }

    path = os.path.join(BASE_PATH, "incidents", f"{incident_id}.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    record_event(
        event_type="incident",
        summary=what,
        storage_path=path
    )

    return data

if __name__ == "__main__":
    inc = save_incident(
        what="文字化け完全修復テスト",
        why="既存CSVエンコード混在",
        how="初期UTF-8非BOM生成",
        countermeasure="CSV再生成とUTF-8-SIG統一",
        recurrence_condition="CSV再生成せず修正のみ実施"
    )
    print("INCIDENT SAVED:", inc)
