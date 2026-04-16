# -*- coding: utf-8 -*-
"""
v1a_aggregated.py
V1a: GPT連続違反4件を1件に集約して間隔を再計算
"""
import csv, datetime
from pathlib import Path

EVENTS_CSV  = Path(r"C:\Users\sirok\MoCKA\data\events.csv")
MOCKA_START = datetime.datetime(2026, 3, 29)
INCIDENT_LEVELS = {"WARNING", "CRITICAL", "ERROR"}

def pdt(s):
    try: return datetime.datetime.fromisoformat(str(s).strip())
    except: return None

def safe(v, k, d=""):
    val = v.get(k)
    return val if val is not None else d

def load():
    with open(EVENTS_CSV, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def stats(lst):
    if not lst: return {"n":0,"mean_h":0,"min_h":0,"max_h":0}
    return {
        "n"     : len(lst),
        "mean_h": round(sum(lst)/len(lst), 2),
        "min_h" : round(min(lst), 2),
        "max_h" : round(max(lst), 2),
    }

def main():
    events = load()
    incs = sorted(
        [e for e in events if safe(e,"risk_level").strip() in INCIDENT_LEVELS and pdt(safe(e,"when"))],
        key=lambda e: pdt(safe(e,"when"))
    )

    # ── 集約処理: INC004-007を1件(INC004のみ)に集約 ──
    AGGREGATE_IDS = {"E20260328_INC005","E20260328_INC006","E20260328_INC007"}
    incs_agg = [e for e in incs if safe(e,"event_id") not in AGGREGATE_IDS]

    print("=== V1a: GPT連続違反集約後のインシデントリスト ===")
    for e in incs_agg:
        ts = pdt(safe(e,"when"))
        phase = "MoCKA前" if ts < MOCKA_START else "MoCKA後"
        print(f"[{phase}] {safe(e,'when')[:16]} | {safe(e,'risk_level'):8} | {safe(e,'title')[:40]}")

    # ── 間隔計算(生) ──
    print("\n=== 間隔詳細(集約後) ===")
    ib_raw, ia_raw = [], []
    prev = None
    for e in incs_agg:
        ts = pdt(safe(e,"when"))
        if prev:
            delta_h = (ts - prev["ts"]).total_seconds() / 3600
            phase = "前→前" if ts < MOCKA_START else ("前→後(境界)" if prev["ts"] < MOCKA_START else "後→後")
            print(f"  {delta_h:6.1f}h ({delta_h/24:.1f}日) | {phase} | {prev['title'][:20]} -> {safe(e,'title')[:20]}")
            if ts < MOCKA_START:
                ib_raw.append(delta_h)
            elif prev["ts"] >= MOCKA_START:
                ia_raw.append(delta_h)
        prev = {"ts": ts, "title": safe(e,"title"), "id": safe(e,"event_id")}

    sb = stats(ib_raw)
    sa = stats(ia_raw)

    print(f"\n=== V1 vs V1a 比較 ===")
    print(f"{'':20} {'V1(生)':>12} {'V1a(集約)':>12}")
    print(f"{'MoCKA前 n':20} {'6':>12} {sb['n']:>12}")
    print(f"{'MoCKA前 平均間隔':20} {'32.5h':>12} {sb['mean_h']:>12}h")
    print(f"{'MoCKA後 n':20} {'3':>12} {sa['n']:>12}")
    print(f"{'MoCKA後 平均間隔':20} {'33.54h':>12} {sa['mean_h']:>12}h")

    if sb["mean_h"] > 0 and sa["mean_h"] > 0:
        ratio = round(sa["mean_h"] / sb["mean_h"], 2)
        print(f"{'改善倍率':20} {'1.03倍':>12} {ratio:>11}倍")
    else:
        ratio = "N/A"
        print(f"{'改善倍率':20} {'1.03倍':>12} {'N/A':>12}")

    # ── 密度比較(集約後) ──
    before_agg = [e for e in incs_agg if pdt(safe(e,"when")) < MOCKA_START]
    after_agg  = [e for e in incs_agg if pdt(safe(e,"when")) >= MOCKA_START]

    b_span = max((pdt(safe(before_agg[-1],"when")) - pdt(safe(before_agg[0],"when"))).days, 1) if len(before_agg)>1 else 1
    a_span = max((pdt(safe(after_agg[-1],"when"))  - pdt(safe(after_agg[0],"when"))).days,  1) if len(after_agg)>1 else 1

    b_density = round(len(before_agg) / b_span * 30, 2)
    a_density = round(len(after_agg)  / a_span * 30, 2)
    density_reduction = round((1 - a_density/b_density)*100, 1) if b_density > 0 else 0

    print(f"\n=== 密度比較(集約後) ===")
    print(f"MoCKA前: {len(before_agg)}件/{b_span}日 = {b_density}件/30日")
    print(f"MoCKA後: {len(after_agg)}件/{a_span}日 = {a_density}件/30日")
    print(f"密度削減率: {density_reduction}%")

    # ── 重大度別分析(V1c) ──
    print(f"\n=== V1c: 重大度別間隔分析 ===")
    for level in ["CRITICAL","WARNING"]:
        lvl_incs = [e for e in incs_agg if safe(e,"risk_level").strip()==level]
        lvl_incs.sort(key=lambda e: pdt(safe(e,"when")))
        intervals = []
        prev2 = None
        for e in lvl_incs:
            ts = pdt(safe(e,"when"))
            if prev2: intervals.append((ts-prev2).total_seconds()/3600)
            prev2 = ts
        s = stats(intervals)
        print(f"  {level}: {len(lvl_incs)}件 平均間隔={s['mean_h']}h")

    print(f"\n=== 論文記述案 ===")
    print(f"V1a(連続違反集約後): 前平均{sb['mean_h']}h → 後平均{sa['mean_h']}h")
    if isinstance(ratio, float):
        print(f"改善倍率: {ratio}倍")
    print(f"密度削減率: {density_reduction}%")
    print(f"※GPT連続違反(INC004-007)は同一制約違反の反復として1事象に集約")

if __name__ == "__main__":
    main()
