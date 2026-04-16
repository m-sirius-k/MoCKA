import os
import sys
import json

sys.path.append(os.path.abspath("."))

from runtime.governance.semantic_engine import detect_semantic_recurrence
from runtime.record.csv_record_engine import record_event
from runtime.governance.loop_guard import check_loop

INCIDENT_PATH = "docs/incidents"

def load_incident_by_id(incident_id):
    path = os.path.join(INCIDENT_PATH, f"{incident_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def self_doubt_process(current_event_text):
    result = detect_semantic_recurrence(current_event_text)

    if not result["recurrence_detected"]:
        return {
            "status": "ok",
            "action": "continue"
        }

    match = result["matches"][0]
    incident_id = match["incident_id"]

    guard = check_loop(incident_id)

    if guard["status"] == "escalation":
        record_event(
            event_type="escalation",
            summary=f"ESCALATED: {incident_id}",
            storage_path=""
        )
        return {
            "status": "escalated",
            "incident_id": incident_id
        }

    incident = load_incident_by_id(incident_id)
    countermeasure = incident.get("Countermeasure", "no countermeasure")

    record_event(
        event_type="self_doubt_trigger",
        summary=f"STOP (semantic) {incident_id}",
        storage_path=""
    )

    return {
        "status": "stopped",
        "incident_id": incident_id,
        "countermeasure": countermeasure,
        "score": match["score"]
    }

if __name__ == "__main__":
    test = "CSV修正をせずにそのまま使ったケース"

    result = self_doubt_process(test)

    print("RESULT:", result)
