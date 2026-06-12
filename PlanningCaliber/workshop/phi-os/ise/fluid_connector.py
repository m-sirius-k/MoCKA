"""ISE → Fluid Coordinate Theory 接続 v1"""

from pathlib import Path

TRAJECTORY_PATH = Path("C:/Users/sirok/MoCKA/data/trajectory.csv")


def compute_delta(before_state: str, after_state: str) -> dict:
    """
    state遷移からΔX/ΔY/ΔZを計算する。
    初期実装はシンプルなルールベース。
    """
    deltas = {
        ("initializing", "active"):   {"dx": +0.05, "dy": +0.10, "dz": +0.05},
        ("active", "degraded"):       {"dx": -0.10, "dy": -0.05, "dz": -0.15},
        ("degraded", "active"):       {"dx": +0.08, "dy": +0.05, "dz": +0.10},
        ("active", "suspended"):      {"dx":  0.00, "dy": -0.05, "dz": -0.05},
        ("suspended", "active"):      {"dx":  0.00, "dy": +0.05, "dz": +0.05},
        ("active", "sealed"):         {"dx": +0.10, "dy": +0.05, "dz": +0.10},
    }
    key = (before_state, after_state)
    return deltas.get(key, {"dx": 0.0, "dy": 0.0, "dz": 0.0})


def notify_trajectory(before: str, after: str, event_id: str) -> bool:
    """trajectory.csvにΔ値を追記する（簡易版）"""
    delta = compute_delta(before, after)
    try:
        with open(TRAJECTORY_PATH, "a", encoding="utf-8") as f:
            from datetime import datetime, timezone
            ts = datetime.now(timezone.utc).isoformat()
            f.write(f"{ts},{event_id},{before},{after},{delta['dx']},{delta['dy']},{delta['dz']}\n")
        return True
    except Exception:
        return False
