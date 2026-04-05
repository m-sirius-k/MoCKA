import csv
import json
from datetime import datetime
from pathlib import Path

INPUT  = Path(r"C:\Users\sirok\MoCKA\data\trajectory.csv")
OUTPUT = Path(r"C:\Users\sirok\MoCKA\data\trajectory_v2.csv")

NEW_FIELDS = ["dt","dX","dY","dZ","speed","trajectory_id"]

rows = []
with open(INPUT, encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames + NEW_FIELDS
    rows = list(reader)

# 時間差・座標差・速度を計算
for i, row in enumerate(rows):
    if i == 0:
        row["dt"]  = 0.0
        row["dX"]  = 0.0
        row["dY"]  = 0.0
        row["dZ"]  = 0.0
        row["speed"] = 0.0
        row["trajectory_id"] = "TRJ_001"
        continue

    prev = rows[i - 1]

    # dt（秒）
    try:
        t1 = datetime.fromisoformat(row["timestamp"])
        t0 = datetime.fromisoformat(prev["timestamp"])
        dt = (t1 - t0).total_seconds()
    except:
        dt = 0.0

    dX = float(row["X"]) - float(prev["X"])
    dY = float(row["Y"]) - float(prev["Y"])
    dZ = float(row["Z"]) - float(prev["Z"])

    speed = (dX**2 + dY**2 + dZ**2)**0.5 / dt if dt > 0 else 0.0

    row["dt"]    = round(dt, 2)
    row["dX"]    = round(dX, 4)
    row["dY"]    = round(dY, 4)
    row["dZ"]    = round(dZ, 4)
    row["speed"] = round(speed, 6)
    row["trajectory_id"] = "TRJ_001"

with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows(rows)

print(f"Done: {len(rows)} rows -> {OUTPUT}")

# 統計サマリー
dZs = [float(r["dZ"]) for r in rows[1:] if r["dZ"]]
dXs = [float(r["dX"]) for r in rows[1:] if r["dX"]]
dYs = [float(r["dY"]) for r in rows[1:] if r["dY"]]
speeds = [float(r["speed"]) for r in rows[1:] if r["speed"]]

print(f"ΔX range: {min(dXs):.4f} ~ {max(dXs):.4f}")
print(f"ΔY range: {min(dYs):.4f} ~ {max(dYs):.4f}")
print(f"ΔZ range: {min(dZs):.4f} ~ {max(dZs):.4f}")
print(f"Speed max: {max(speeds):.6f}")
print(f"Speed mean: {sum(speeds)/len(speeds):.6f}")
