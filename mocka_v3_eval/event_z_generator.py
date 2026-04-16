import csv
from pathlib import Path
from datetime import datetime

# =========================
# 設定
# =========================
EVENTS_PATH = Path(r"C:\Users\sirok\MoCKA\data\events.csv")
OUTPUT_PATH = Path(r"C:\Users\sirok\MoCKA\data\event_z_scores.csv")

MOCKA_START = datetime(2026, 3, 29)

# =========================
# Z軸構成要素
# =========================

def calc_D(row):
    """逸脱度"""
    risk = row.get("risk_level", "").lower()
    
    if risk == "critical":
        return 1.0
    elif risk == "warning":
        return 0.7
    else:
        return 0.3

def calc_R(row):
    """再発性（仮：未接続）"""
    return 0.0

def calc_T(row):
    """応答遅延（仮：未実装）"""
    return 0.0

def calc_Z(D, R, T, wD=0.4, wR=0.3, wT=0.3):
    return 1 - (wD*D + wR*R + wT*T)

# =========================
# メイン処理
# =========================

rows_out = []

with open(EVENTS_PATH, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        when_str = row.get("when", "")
        if not when_str:
            continue
        
        try:
            when = datetime.fromisoformat(when_str.replace("Z", ""))
        except:
            continue
        
        D = calc_D(row)
        R = calc_R(row)
        T = calc_T(row)
        Z = calc_Z(D, R, T)
        
        phase = "after" if when >= MOCKA_START else "before"
        
        rows_out.append({
            "event_id": row.get("event_id"),
            "when": when_str,
            "phase": phase,
            "risk_level": row.get("risk_level"),
            "D": round(D, 4),
            "R": R,
            "T": T,
            "Z": round(Z, 4)
        })

# =========================
# 保存
# =========================

with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
    fieldnames = ["event_id", "when", "phase", "risk_level", "D", "R", "T", "Z"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows_out)

print("===================================")
print(f"生成完了: {OUTPUT_PATH}")
print(f"総イベント数: {len(rows_out)}")

# =========================
# 集計
# =========================

before = [r["Z"] for r in rows_out if r["phase"] == "before"]
after  = [r["Z"] for r in rows_out if r["phase"] == "after"]

def mean(x):
    return sum(x)/len(x) if x else 0

print("\n=== Z統計 ===")
print(f"Before n={len(before)} mean={mean(before):.4f}")
print(f"After  n={len(after)} mean={mean(after):.4f}")
print(f"ΔZ = {mean(after)-mean(before):.4f}")