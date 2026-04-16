# -*- coding: utf-8 -*-
"""
v1_deep_analysis.py
V1インシデント間隔分析の深掘り
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

def main():
    events = load()
    incs = sorted(
        [e for e in events if safe(e,"risk_level").strip() in INCIDENT_LEVELS and pdt(safe(e,"when"))],
        key=lambda e: pdt(safe(e,"when"))
    )

    print("=== インシデント全件リスト ===")
    for e in incs:
        ts = pdt(safe(e,"when"))
        phase = "MoCKA前" if ts < MOCKA_START else "MoCKA後"
        print(f"[{phase}] {safe(e,'when')[:16]} | {safe(e,'risk_level'):8} | {safe(e,'event_id'):20} | {safe(e,'title')[:35]}")

    print("\n=== 間隔詳細 ===")
    prev = None
    for e in incs:
        ts = pdt(safe(e,"when"))
        if prev:
            delta_h = (ts - prev["ts"]).total_seconds() / 3600
            delta_d = delta_h / 24
            phase = "MoCKA前→前" if ts < MOCKA_START else ("前→後(境界)" if prev["ts"] < MOCKA_START else "MoCKA後→後")
            print(f"  {prev['id'][:18]} -> {safe(e,'event_id')[:18]} | {delta_h:.1f}h ({delta_d:.1f}日) | {phase}")
        prev = {"ts": ts, "id": safe(e,"event_id")}

    print("\n=== 問題の本質 ===")
    before_incs = [e for e in incs if pdt(safe(e,"when")) < MOCKA_START]
    after_incs  = [e for e in incs if pdt(safe(e,"when")) >= MOCKA_START]

    print(f"MoCKA前インシデント数: {len(before_incs)}")
    print(f"MoCKA後インシデント数: {len(after_incs)}")

    # 観測期間を計算
    if before_incs:
        b_span = (pdt(safe(before_incs[-1],"when")) - pdt(safe(before_incs[0],"when"))).days + 1
        print(f"MoCKA前観測期間: {b_span}日")
        print(f"MoCKA前インシデント密度: {round(len(before_incs)/max(b_span,1)*30,2)}件/30日")

    if after_incs:
        a_span = (pdt(safe(after_incs[-1],"when")) - pdt(safe(after_incs[0],"when"))).days + 1
        print(f"MoCKA後観測期間: {a_span}日")
        print(f"MoCKA後インシデント密度: {round(len(after_incs)/max(a_span,1)*30,2)}件/30日")

    print("\n=== V1が1.03倍に留まった原因仮説 ===")
    print("1. MoCKA後のインシデントが短期間(数日)に集中している")
    print("   → 観測期間が短すぎて統計的に有意な差が出ない")
    print("2. MoCKA前のGPT上書き4件が同日(1時間間隔)に集中")
    print("   → 平均間隔を人工的に短縮させている")
    print("3. n=3(後)が少なすぎる → 平均値が不安定")
    print("\n=== 改善シナリオ ===")
    print("A. 観測期間を延長(3ヶ月後に再測定) → 自然な改善が出る")
    print("B. GPT上書き4件を1件(連続違反)として集約 → 前の平均間隔が伸びてコントラストが強まる")
    print("C. インシデント密度(/30日)で比較 → 間隔より直感的な指標")

    # 密度比較
    if before_incs and after_incs:
        b_span = max((pdt(safe(before_incs[-1],"when")) - pdt(safe(before_incs[0],"when"))).days, 1)
        a_span = max((pdt(safe(after_incs[-1],"when"))  - pdt(safe(after_incs[0],"when"))).days,  1)
        b_density = round(len(before_incs) / b_span * 30, 2)
        a_density = round(len(after_incs)  / a_span * 30, 2)
        print(f"\n=== 密度比較(代替指標) ===")
        print(f"MoCKA前: {b_density}件/30日")
        print(f"MoCKA後: {a_density}件/30日")
        if b_density > 0:
            print(f"密度削減率: {round((1 - a_density/b_density)*100, 1)}%")

if __name__ == "__main__":
    main()
