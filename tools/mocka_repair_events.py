import csv
import os
import shutil
from datetime import datetime

EVENTS = r"C:\Users\sirok\MoCKA\data\events.csv"
CORRUPTED = r"C:\Users\sirok\MoCKA\data\events_corrupted.csv"
BACKUP = r"C:\Users\sirok\MoCKA\data\events_backup_{}.csv".format(
    datetime.now().strftime("%Y%m%d_%H%M%S"))

FIELDNAMES = [
    "event_id","when","who_actor","what_type",
    "where_component","where_path","why_purpose","how_trigger",
    "channel_type","lifecycle_phase","risk_level",
    "category_ab","target_class","title","short_summary",
    "before_state","after_state","change_type",
    "impact_scope","impact_result","related_event_id","trace_id","free_note"
]

# バックアップ
shutil.copy(EVENTS, BACKUP)
print(f"[backup] {BACKUP}")

normal = []
corrupted = []

with open(EVENTS, encoding="utf-8", errors="replace") as f:
    reader = csv.reader(f)
    for row in reader:
        if not row:
            continue
        # ヘッダー行
        if row[0] == "event_id":
            continue
        # 正規フォーマット判定：23列 or who_actorが含まれる
        if len(row) >= 20 and (row[2] in ("mocka_router", "human_nsjsiro")):
            normal.append(row)
        else:
            corrupted.append(row)

print(f"[正規行] {len(normal)}件")
print(f"[異常行] {len(corrupted)}件")

# 正規行を書き戻す
with open(EVENTS, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(FIELDNAMES)
    for row in normal:
        # 23列に調整
        while len(row) < 23:
            row.append("N/A")
        writer.writerow(row[:23])

# 異常行を退避
with open(CORRUPTED, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["raw_data"])
    for row in corrupted:
        writer.writerow(row)

print(f"[完了] events.csv: {len(normal)}件に整理")
print(f"[退避] events_corrupted.csv: {len(corrupted)}件")
