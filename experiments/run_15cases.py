import subprocess, sys, os, json, csv
from datetime import datetime
from pathlib import Path

BASE = Path(r"C:\Users\sirok\MoCKA")
EXP  = BASE / "experiments" / "run_experiment_A_v2.py"
OUT  = BASE / "experiments" / "results"
OUT.mkdir(exist_ok=True)

CASES = [
    ("A", str(BASE / "data" / "events.csv"),                      "MoCKA Event Log"),
    ("B", str(BASE / "experiments" / "plant_doc_A.txt"),          "Plant Document"),
    ("C", str(BASE / "experiments" / "combined_raw_all.txt"),     "Combined Raw All"),
    ("D", str(BASE / "experiments" / "human_doc_004.txt"),        "Human Doc 004"),
    ("E", str(BASE / "experiments" / "net_docs_combined.txt"),    "Net Docs Baseline"),
]

summary = []
print("\n" + "="*60)
print("  MoCKA 15-Case Experiment Run")
print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("="*60)

for case_id, filepath, label in CASES:
    if not Path(filepath).exists():
        print(f"\n[SKIP] {label} — file not found: {filepath}")
        continue
    for run in range(1, 4):
        eid = f"EXP_{case_id}_Run{run}"
        print(f"\n>>> {eid} : {label}")
        result = subprocess.run(
            [sys.executable, str(EXP), filepath, eid],
            capture_output=True, text=True, encoding="utf-8"
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"[ERROR] {result.stderr}")
            continue

        # 結果JSONを読み込んでサマリーに追加
        today = datetime.now().strftime("%Y%m%d")
        jpath = OUT / f"{eid}_{today}.json"
        if jpath.exists():
            with open(jpath, encoding="utf-8") as f:
                d = json.load(f)
            summary.append({
                "experiment_id": eid,
                "label": label,
                "run": run,
                "recovery_rate": d.get("recovery_rate"),
                "weighted_rr": d.get("weighted_recovery_rate"),
                "missing": d.get("missing_stages", [])
            })

# サマリー出力
print("\n" + "="*60)
print("  SUMMARY — 15 Cases")
print("="*60)
print(f"  {'ID':<18} {'Label':<22} {'RR':>6} {'WRR':>6}")
print("  " + "-"*54)
for s in summary:
    print(f"  {s['experiment_id']:<18} {s['label']:<22} {str(s['recovery_rate'])+'%':>6} {str(s['weighted_rr'])+'%':>6}")

rrs = [s["recovery_rate"] for s in summary if s["recovery_rate"] is not None]
if rrs:
    print(f"\n  Mean RR  : {sum(rrs)/len(rrs):.1f}%")
    print(f"  Max RR   : {max(rrs):.1f}%")
    print(f"  Min RR   : {min(rrs):.1f}%")
    print(f"  N        : {len(rrs)}")

# サマリーJSON保存
summary_path = OUT / f"15case_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(summary_path, "w", encoding="utf-8") as f:
    json.dump({"total": len(summary), "mean_rr": sum(rrs)/len(rrs) if rrs else 0,
               "cases": summary, "timestamp": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)
print(f"\n  Summary saved: {summary_path}")
print("="*60)
