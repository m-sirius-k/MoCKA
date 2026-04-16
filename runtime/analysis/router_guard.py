# router_guard.py
# Phase5-B2: 連続上昇対応版

import json
import os

CALIBER_STATE_PATH = r"C:\Users\sirok\MoCKA\runtime\state\caliber_state.json"

def load_caliber():
    if not os.path.exists(CALIBER_STATE_PATH):
        return {}
    with open(CALIBER_STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def decide_route(caliber):
    mode = caliber.get("mode", "NORMAL")
    drift = caliber.get("drift_prediction", {})
    delta = drift.get("delta", 0)

    # 強制制御（連続上昇の最終段）
    if mode == "CAUTION":
        return {
            "route": "SAFE",
            "action": "LIMIT_EXECUTION",
            "reason": "Drift PRE-WARNING (trend)"
        }

    # 上昇中 + Δが一定以上
    elif mode == "WATCH" and delta > 0.2:
        return {
            "route": "CONTROLLED",
            "action": "THROTTLE_EXECUTION",
            "reason": "Drift rising with momentum"
        }

    # 通常上昇
    elif mode == "WATCH":
        return {
            "route": "CONTROLLED",
            "action": "REDUCE_VARIATION",
            "reason": "Drift rising"
        }

    # 安定
    else:
        return {
            "route": "NORMAL",
            "action": "FULL_EXECUTION",
            "reason": "Stable"
        }

def main():
    caliber = load_caliber()
    decision = decide_route(caliber)

    print(f"[RouterGuard] route={decision['route']} / action={decision['action']} / reason={decision['reason']}")

if __name__ == "__main__":
    main()
