import os
import json
import re

INCIDENT_PATH = "docs/incidents"
THRESHOLD = 0.5

def tokenize(text):
    # 日本語簡易分解（記号除去＋空白分割）
    text = re.sub(r"[^\w\s]", "", text)
    return set(text.split())

def similarity(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

def load_incidents():
    incidents = []
    if not os.path.exists(INCIDENT_PATH):
        return incidents

    for file in os.listdir(INCIDENT_PATH):
        if file.endswith(".json"):
            path = os.path.join(INCIDENT_PATH, file)
            with open(path, "r", encoding="utf-8") as f:
                incidents.append(json.load(f))
    return incidents

def detect_semantic_recurrence(current_text):
    incidents = load_incidents()

    current_tokens = tokenize(current_text)

    matches = []

    for inc in incidents:
        condition = inc.get("RecurrenceCondition", "")
        tokens = tokenize(condition)

        score = similarity(current_tokens, tokens)

        if score >= THRESHOLD:
            matches.append({
                "incident_id": inc.get("id"),
                "score": score,
                "condition": condition
            })

    return {
        "recurrence_detected": len(matches) > 0,
        "matches": sorted(matches, key=lambda x: x["score"], reverse=True)
    }

if __name__ == "__main__":
    test = "CSV修正をせずにそのまま使ったケース"

    result = detect_semantic_recurrence(test)

    print("RESULT:", result)
