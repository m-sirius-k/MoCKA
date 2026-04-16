import os
import json

INCIDENT_DIR = "docs/incidents"


def normalize(text):
    if not text:
        return ""
    # 簡易正規化（空白・改行除去）
    return text.replace(" ", "").replace("\n", "").replace("\r", "")


def load_incidents():
    incidents = []

    if not os.path.exists(INCIDENT_DIR):
        return incidents

    for f in os.listdir(INCIDENT_DIR):
        if f.endswith(".json"):
            path = os.path.join(INCIDENT_DIR, f)
            try:
                with open(path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    incidents.append(data)
            except:
                continue

    return incidents


def check_preventive(event_text):
    incidents = load_incidents()

    e = normalize(event_text)

    for inc in incidents:
        condition = normalize(inc.get("RecurrenceCondition", ""))

        # ★ 強化：部分一致（双方向）
        if condition and (condition in e or e in condition):
            return {
                "prevented": True,
                "incident_id": inc.get("id"),
                "action": inc.get("Countermeasure")
            }

    return {"prevented": False}


def apply_preventive_rule(result):
    if not result.get("prevented"):
        return {"status": "ok"}

    return {
        "status": "prevented",
        "incident_id": result.get("incident_id"),
        "action": result.get("action")
    }
