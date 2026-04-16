# drift_predictor.py
# Phase5-B2: 連続上昇検知対応

import json
import os
from datetime import datetime, UTC

LEDGER_PATH = r"C:\Users\sirok\MoCKA\runtime\record\event_log.json"
OUTPUT_PATH = r"C:\Users\sirok\MoCKA\runtime\state\drift_state.json"

def load_ledger():
    if not os.path.exists(LEDGER_PATH):
        return []
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

def extract_drift(events):
    vals = []
    for e in events:
        if isinstance(e, dict):
            d = e.get("drift")
            if isinstance(d, (int, float)):
                vals.append(d)
    return vals

def calc_delta_series(vals):
    if len(vals) < 2:
        return []

    deltas = []
    for i in range(1, len(vals)):
        deltas.append(vals[i] - vals[i-1])
    return deltas

def detect_trend(deltas):
    if len(deltas) < 3:
        return "STABLE"

    last3 = deltas[-3:]

    # 3連続上昇
    if all(d > 0 for d in last3):
        if sum(last3) > 0.5:
            return "PRE-WARNING"
        return "RISING"

    # 微増
    if deltas[-1] > 0:
        return "RISING"

    return "STABLE"

def save_state(delta, status):
    state = {
        "timestamp": datetime.now(UTC).isoformat(),
        "delta_drift": delta,
        "status": status
    }
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def main():
    events = load_ledger()
    vals = extract_drift(events)
    deltas = calc_delta_series(vals)

    delta = deltas[-1] if deltas else 0.0
    status = detect_trend(deltas)

    print(f"[DriftPredictor] ΔDrift={delta:.3f} / {status}")
    save_state(delta, status)

if __name__ == "__main__":
    main()
