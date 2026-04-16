# dashboard_drift_view.py
# Phase5-B1: Drift状態の可視化

import json
import os

CALIBER_STATE_PATH = r"C:\Users\sirok\MoCKA\runtime\state\caliber_state.json"

def load_caliber():
    if not os.path.exists(CALIBER_STATE_PATH):
        return None
    with open(CALIBER_STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def render(caliber):
    if caliber is None:
        print("[Dashboard] No data")
        return

    mode = caliber.get("mode", "UNKNOWN")
    drift = caliber.get("drift_prediction", {})

    print("====== MoCKA Drift Dashboard ======")
    print(f"MODE        : {mode}")
    print(f"ΔDRIFT      : {drift.get('delta', 0)}")
    print(f"STATUS      : {drift.get('status', 'UNKNOWN')}")
    print("===================================")

def main():
    caliber = load_caliber()
    render(caliber)

if __name__ == "__main__":
    main()
