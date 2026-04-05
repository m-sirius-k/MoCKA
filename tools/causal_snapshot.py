import csv
import json
from datetime import datetime
from pathlib import Path

TRAJ   = Path(r"C:\Users\sirok\MoCKA\data\trajectory_v2.csv")
OUTPUT = Path(r"C:\Users\sirok\MoCKA\data\causal_snapshots.json")

SPEED_THRESHOLD = 0.5   # この速度を超えたらインシデント候補
PRE_N  = 3              # 事故前N件
POST_N = 3              # 事故後N件

rows = []
with open(TRAJ, encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))

snapshots = []
for i, row in enumerate(rows):
    speed = float(row.get("speed", 0) or 0)
    if speed < SPEED_THRESHOLD:
        continue

    pre   = rows[max(0, i - PRE_N) : i]
    post  = rows[i + 1 : i + 1 + POST_N]

    snap = {
        "snapshot_id"   : f"SNAP_{row['event_id']}",
        "trigger_event" : row["event_id"],
        "trigger_time"  : row["timestamp"],
        "trigger_speed" : round(speed, 6),
        "trigger_coord" : {"X": row["X"], "Y": row["Y"], "Z": row["Z"]},
        "delta"         : {"dX": row["dX"], "dY": row["dY"], "dZ": row["dZ"]},
        "pre_events"    : [{"event_id": r["event_id"], "timestamp": r["timestamp"],
                            "what_type": r["what_type"], "X": r["X"], "Y": r["Y"], "Z": r["Z"]} for r in pre],
        "post_events"   : [{"event_id": r["event_id"], "timestamp": r["timestamp"],
                            "what_type": r["what_type"], "X": r["X"], "Y": r["Y"], "Z": r["Z"]} for r in post],
        "causal_chain"  : [r["event_id"] for r in pre] + [row["event_id"]] + [r["event_id"] for r in post]
    }
    snapshots.append(snap)

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump({"total": len(snapshots), "threshold": SPEED_THRESHOLD,
               "snapshots": snapshots}, f, ensure_ascii=False, indent=2)

print(f"Snapshots detected: {len(snapshots)}")
for s in snapshots[:5]:
    print(f"  {s['snapshot_id']} | speed={s['trigger_speed']} | "
          f"dZ={s['delta']['dZ']} | {s['trigger_time']}")
