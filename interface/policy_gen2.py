import csv, json
from datetime import datetime
from pathlib import Path

BASE              = Path("C:/Users/sirok/MoCKA")
RECURRENCE_CSV    = BASE / "data/recurrence_registry.csv"
POLICY_CANDIDATES = BASE / "data/policy_candidates.json"
DISTRIBUTION_JSON = BASE / "data/distribution_state.json"

WARN_THRESHOLD = 3

TEMPLATES = {
    "INSTRUCTION_IGNORE": {
        "title": "ファイル保護条項の制度化",
        "proposals": [
            "MoCKA憲章に編集禁止ファイル保護条項を追加する",
            "write操作前にSHA-256ハッシュを検証する",
            "不一致時はきむら博士の承認なしに書き込みを禁止する",
        ],
        "priority": "critical",
    },
    "save": {
        "title": "router.save再発防止制度",
        "proposals": [
            "save処理のエラーハンドリングを強化しスタックトレースを記録する",
            "save失敗時はFAST_WRONGイベントを自動生成する",
            "saveの成功/失敗を必ずcategory_abに記録する",
        ],
        "priority": "high",
    },
    "collaboration": {
        "title": "collaboration再発防止制度",
        "proposals": [
            "collaboration処理のタイムアウトを設定しSLOW_DRIFTを検出する",
            "collaboration失敗時は自動リトライ1回後にイベント記録する",
        ],
        "priority": "medium",
    },
}

def load_counts():
    counts = {}
    with open(RECURRENCE_CSV, encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            wt = row.get("what_type", "").strip()
            if len(wt) > 30:
                wt = "INSTRUCTION_IGNORE"
            if wt:
                counts[wt] = counts.get(wt, 0) + 1
    return counts

def main():
    print("=" * 50)
    print("policy_gen2.py — 制度改善候補生成")
    print("=" * 50)

    counts = load_counts()
    print("\n--- 正規化カウント ---")
    for k, v in sorted(counts.items(), key=lambda x: -x[1]):
        warn = " WARN" if v >= WARN_THRESHOLD else ""
        print(f"  {k:<25} {v:>3}件{warn}")

    dist = {}
    if DISTRIBUTION_JSON.exists():
        with open(DISTRIBUTION_JSON, encoding="utf-8") as f:
            dist = json.load(f)
    z_mean = dist.get("coordinate", {}).get("Z", {}).get("mean", 1.0)

    candidates = []
    today = datetime.now().strftime("%Y%m%d")

    for dt, count in sorted(counts.items(), key=lambda x: -x[1]):
        if count >= WARN_THRESHOLD and dt in TEMPLATES:
            t = TEMPLATES[dt]
            cid = "PC_" + dt + "_" + today
            candidates.append({
                "id": cid,
                "generated_at": datetime.now().isoformat(),
                "deviation_type": dt,
                "recurrence_count": count,
                "title": t["title"],
                "proposals": t["proposals"],
                "priority": t["priority"],
                "status": "PENDING_APPROVAL",
                "approved_by": None,
                "approved_at": None,
            })
            print(f"\n  [{t['priority'].upper()}] {t['title']} ({count}件)")
            for p in t["proposals"]:
                print(f"    -> {p}")

    if z_mean < 0.80:
        cid = "PC_Z_DRIFT_" + today
        candidates.append({
            "id": cid,
            "generated_at": datetime.now().isoformat(),
            "deviation_type": "Z_AXIS_DRIFT",
            "recurrence_count": 0,
            "title": "制度整合性回復プログラム",
            "proposals": [
                "Z軸が0.75を下回った場合にWARNイベントを自動生成する",
                "recurrence_registryを週次分析し制度改善を継続実施する",
                "OVERVIEW.jsonのcurrent_phaseにZ軸状態を反映する",
            ],
            "priority": "high",
            "status": "PENDING_APPROVAL",
            "approved_by": None,
            "approved_at": None,
        })
        print(f"\n  [HIGH] 制度整合性回復プログラム (Z={z_mean})")

    with open(POLICY_CANDIDATES, "w", encoding="utf-8") as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*50}")
    print(f"HUMAN GATE — {len(candidates)}件の制度改善候補")
    print(f"{'='*50}")
    for c in candidates:
        print(f"  [{c['priority'].upper()}] {c['id']}")
        print(f"    {c['title']}")
    print(f"\n承認コマンド:")
    for c in candidates:
        print(f"  python interface/policy_gen2.py --approve {c['id']}")
    print(f"\n出力: {POLICY_CANDIDATES}")

def approve(policy_id):
    with open(POLICY_CANDIDATES, encoding="utf-8") as f:
        candidates = json.load(f)
    for c in candidates:
        if c["id"] == policy_id:
            c["status"] = "APPROVED"
            c["approved_by"] = "nsjp_kimura"
            c["approved_at"] = datetime.now().isoformat()
            print(f"承認: {c['title']}")
    with open(POLICY_CANDIDATES, "w", encoding="utf-8") as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3 and sys.argv[1] == "--approve":
        approve(sys.argv[2])
    else:
        main()
