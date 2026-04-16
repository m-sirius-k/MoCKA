# -*- coding: utf-8 -*-
"""
recurrence_join.py
recurrence_registryとeventsを日時近似で結合し
正しいCRS・再発パターンを算出する
"""
import csv, datetime
from pathlib import Path
from collections import defaultdict

ROOT = Path(r"C:\Users\sirok\MoCKA\data")

def pdt(s):
    try: return datetime.datetime.fromisoformat(str(s).strip().replace('t','T'))
    except: return None

def load(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

events     = load(ROOT/"events.csv")
recurrence = load(ROOT/"recurrence_registry.csv")

print(f"events: {len(events)}件")
print(f"recurrence: {len(recurrence)}件")

# ── 日時±5分で近似結合 ──────────────────────────────
WINDOW = 300  # 秒

ev_by_time = [(pdt(e.get("when","")), e) for e in events if pdt(e.get("when",""))]

matched = []
unmatched = []

for r in recurrence:
    rt = pdt(r.get("current_when",""))
    if not rt:
        unmatched.append(r)
        continue
    # ±5分以内のeventsを探す
    candidates = [(abs((rt-et).total_seconds()), e) for et,e in ev_by_time if abs((rt-et).total_seconds()) <= WINDOW]
    if candidates:
        best = min(candidates, key=lambda x: x[0])
        matched.append({"recurrence": r, "event": best[1], "delta_sec": best[0]})
    else:
        unmatched.append(r)

print(f"\n結合結果:")
print(f"  一致: {len(matched)}件")
print(f"  未一致: {len(unmatched)}件")

# ── 結合結果の分析 ──────────────────────────────────
print(f"\n=== 再発イベントの詳細 ===")
risk_dist  = defaultdict(int)
type_dist  = defaultdict(int)
actor_dist = defaultdict(int)
recur_count_dist = defaultdict(int)

for m in matched:
    e = m["event"]
    r = m["recurrence"]
    risk  = e.get("risk_level","normal")
    wtype = e.get("what_type","unknown")
    actor = e.get("who_actor","unknown")
    rcount = r.get("recurrence_count","1")
    risk_dist[risk] += 1
    type_dist[wtype] += 1
    actor_dist[actor] += 1
    recur_count_dist[rcount] += 1
    print(f"  [{risk}] {e.get('event_id','?'):20} | {wtype:15} | {actor:20} | 再発回数={rcount} | Δ{m['delta_sec']:.0f}s")

print(f"\n=== 集計 ===")
print(f"risk_level分布: {dict(risk_dist)}")
print(f"what_type分布 : {dict(type_dist)}")
print(f"who_actor分布 : {dict(actor_dist)}")
print(f"recurrence_count分布: {dict(recur_count_dist)}")

# ── CRS再計算 ──────────────────────────────────────
INCIDENT_LEVELS = {"WARNING","CRITICAL","ERROR"}
inc_all = [e for e in events if e.get("risk_level","").strip() in INCIDENT_LEVELS]
rec_inc = [m for m in matched if m["event"].get("risk_level","").strip() in INCIDENT_LEVELS]

CRS = round(len(rec_inc)/max(len(inc_all),1)*100, 2)
print(f"\n=== 修正CRS ===")
print(f"全インシデント: {len(inc_all)}件")
print(f"再発かつインシデント: {len(rec_inc)}件")
print(f"CRS（修正値）: {CRS}%")

# ── 再発パターン分析 ──────────────────────────────
print(f"\n=== 再発パターン（what_type別） ===")
pattern = defaultdict(lambda: {"count":0,"avg_recur":[]})
for m in matched:
    wt = m["recurrence"].get("what_type","unknown")
    pattern[wt]["count"] += 1
    try: pattern[wt]["avg_recur"].append(int(m["recurrence"].get("recurrence_count",1)))
    except: pass

for wt, v in sorted(pattern.items(), key=lambda x: x[1]["count"], reverse=True):
    avg = round(sum(v["avg_recur"])/len(v["avg_recur"]),1) if v["avg_recur"] else "?"
    print(f"  {wt:20}: {v['count']}件 平均再発回数={avg}")

# ── MoCKA前後の再発率比較 ──────────────────────────
MOCKA_START = datetime.datetime(2026,3,29)
rec_before = [m for m in matched if pdt(m["recurrence"].get("current_when","")) and pdt(m["recurrence"].get("current_when","")) < MOCKA_START]
rec_after  = [m for m in matched if pdt(m["recurrence"].get("current_when","")) and pdt(m["recurrence"].get("current_when","")) >= MOCKA_START]

print(f"\n=== MoCKA前後の再発件数 ===")
print(f"MoCKA前: {len(rec_before)}件")
print(f"MoCKA後: {len(rec_after)}件")
print(f"削減率 : {round((1-len(rec_after)/max(len(rec_before),1))*100,1)}%")
