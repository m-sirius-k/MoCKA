# caliber_drift_bridge.py
# Phase5-B1: Drift予兆 → Caliber-B連動

import json
import os

DRIFT_STATE_PATH = r"C:\Users\sirok\MoCKA\runtime\state\drift_state.json"
CALIBER_OUTPUT_PATH = r"C:\Users\sirok\MoCKA\runtime\state\caliber_state.json"

def load_drift():
    if not os.path.exists(DRIFT_STATE_PATH):
        return None
    with open(DRIFT_STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_caliber():
    if not os.path.exists(CALIBER_OUTPUT_PATH):
        return {}
    with open(CALIBER_OUTPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def merge(caliber, drift):
    if drift is None:
        return caliber

    caliber["drift_prediction"] = {
        "delta": drift.get("delta_drift", 0),
        "status": drift.get("status", "UNKNOWN")
    }

    # 予兆に応じた強制フラグ
    if drift.get("status") == "PRE-WARNING":
        caliber["mode"] = "CAUTION"
    elif drift.get("status") == "RISING":
        caliber["mode"] = "WATCH"
    else:
        caliber["mode"] = "NORMAL"

    return caliber

def save(caliber):
    os.makedirs(os.path.dirname(CALIBER_OUTPUT_PATH), exist_ok=True)
    with open(CALIBER_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(caliber, f, indent=2, ensure_ascii=False)

def main():
    drift = load_drift()
    caliber = load_caliber()
    updated = merge(caliber, drift)

    print(f"[CaliberBridge] mode={updated.get('mode')} / drift={updated.get('drift_prediction')}")
    save(updated)

if __name__ == "__main__":
    main()
