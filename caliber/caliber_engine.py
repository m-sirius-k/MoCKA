import json
import os
from datetime import datetime

BASE_PATH = r"C:\Users\sirok\MoCKA"
LEDGER_PATH = os.path.join(BASE_PATH, "runtime", "record", "event_log.csv")

def parse_event_log():
    if not os.path.exists(LEDGER_PATH):
        print("LOG NOT FOUND:", LEDGER_PATH)
        return []

    with open(LEDGER_PATH, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()

    print(f"LOG LINES: {len(lines)}")
    return lines[1:] if len(lines) > 1 else []

def analyze_events(events):
    total = len(events)
    errors = sum(1 for e in events if "error" in e.lower())
    fixes = sum(1 for e in events if "fix" in e.lower())

    print(f"ANALYZE → total:{total}, errors:{errors}, fixes:{fixes}")

    return total, errors, fixes

def calculate_scores(total, errors, fixes):
    if total == 0:
        return {"L":0,"E":0,"A":0,"P":0,"C":0,"R":0,"D":5}

    L = max(0, 5 - errors)
    E = 5 if errors == 0 else 3
    A = min(5, fixes + 2)
    P = min(5, total // 2 + 1)
    C = max(0, 5 - errors * 2)
    R = max(0, 5 - errors)
    D = min(5, errors + (total // 5))

    return {"L":L,"E":E,"A":A,"P":P,"C":C,"R":R,"D":D}

def classify(drift):
    if drift <= 1.5:
        return "NORMAL"
    elif drift <= 3.0:
        return "WARNING"
    elif drift <= 4.0:
        return "DANGER"
    else:
        return "CRITICAL"

def main():
    events = parse_event_log()
    total, errors, fixes = analyze_events(events)
    scores = calculate_scores(total, errors, fixes)

    result = {
        "timestamp": datetime.now().isoformat(),
        "scores": scores,
        "status": classify(scores["D"])
    }

    print("=== Caliber Evaluation (REAL) ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
