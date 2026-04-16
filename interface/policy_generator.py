"""
MoCKA policy_generator.py
制度改善エンジン + Human Gate
Day4実装 - TODO_015

Z軸低下・INSTRUCTION_IGNORE WARN超過を受けて
制度改善候補をJSON差分として生成し、きむら博士の承認を待つ。
"""
import csv, json
from datetime import datetime
from pathlib import Path

BASE              = Path("C:/Users/sirok/MoCKA")
DISTRIBUTION_JSON = BASE / "data/distribution_state.json"
RECURRENCE_CSV    = BASE / "data/recurrence_registry.csv"
POLICY_CANDIDATES = BASE / "data/policy_candidates.json"

WARN_THRESHOLD   = 3
POLICY_THRESHOLD = 5

POLICY_TEMPLATES = {
    "INSTRUCTION_IGNORE": {
        "title":    "ファイル保護条項の制度化",
        "trigger":  "INSTRUCTION_IGNORE が WARN閾値を超過",
        "proposal": [
            "MoCKA憲章に『編集禁止ファイル保護条項』を追加する",
            "mocka_mcp_server.pyへのwrite操作前にSHA-256ハッシュを検証する",
            "不一致の場合はきむら博士の明示的承認なしに書き込みを禁止する",
            "違反発生時は即座にINSTRUCTION_IGNOREイベントを自動記録する",
        ],
        "target_files": ["mocka_mcp_server.py", "interface/router.py", "app.py"],
        "priority":  "critical",
    },
    "PROTOCOL_SKIP": {
        "title":    "セッション開始プロトコルの強制化",
        "trigger":  "PROTOCOL_SKIP が WARN閾値を超過",
        "proposal": [
            "orchestratorはmocka_get_overviewを呼ぶまで作業開始を禁止する",
            "TODO_IDが未指定の場合は作業実行を自動ブロックする",
            "セッション開始ログをevents.csvに必須記録する",
        ],
        "target_files": ["tools/mocka_orchestra_v10.py"],
        "priority":  "medium",
    },
    "SCOPE_CREEP": {
        "title":    "作業スコープ事前承認制度",
        "trigger":  "SCOPE_CREEP が WARN閾値を超過",
        "proposal": [
            "TODO_IDの範囲外ファイルへの変更はきむら博士の承認を必須とする",
            "変更対象ファイル一覧を作業開始前にevents.csvに記録する",
        ],
        "target_files": ["interface/router.py"],
        "priority":  "high",
    },
}

def load_recurrence_counts():
    counts = {}
    if not RECURRENCE_CSV.exists():
        return counts
    try:
        with open(RECURRENCE_CSV, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                dt = row.get("deviation_type","")
                if dt:
                    counts[dt] = counts.get(dt,0) + 1
    except:
        pass
    return counts

def load_distribution():
    if not DISTRIBUTION_JSON.exists():
        return {}
    with open(DISTRIBUTION_JSON, encoding="utf-8") as f:
        return json.load(f)

def generate():
    print("="*55)
    print("MoCKA policy_generator.py Day4")
    print("制度改善候補 生成 + Human Gate")
    print("="*55)

    counts = load_recurrence_counts()
    dist   = load_distribution()
    candidates = []

    print(f"\n--- 再発カウント確認 ---")
    for dt, c in sorted(counts.items(), key=lambda x: -x[1]):
        status = ""
        if c >= POLICY_THRESHOLD: status = "🔴 POLICY発動"
        elif c >= WARN_THRESHOLD: status = "⚠  WARN"
        print(f"  {dt:<25} {c:>3}件  {status}")

    # Z軸低下チェック
    z_mean = dist.get("coordinate",{}).get("Z",{}).get("mean", 1.0)
    z_stab = dist.get("coordinate",{}).get("Z",{}).get("stability","")
    z_alert = z_mean < 0.75 or z_stab == "揺らぎあり"

    print(f"\n--- Z軸（制度整合性）状態 ---")
    print(f"  平均={z_mean}  安定性={z_stab}")
    print(f"  アラート: {'⚠ Z軸低下検出' if z_alert else 'OK'}")

    # 候補生成
    print(f"\n--- 制度改善候補 生成 ---")
    for dt, count in counts.items():
        if count >= WARN_THRESHOLD and dt in POLICY_TEMPLATES:
            tmpl = POLICY_TEMPLATES[dt]
            candidate = {
                "id":            f"PC_{dt}_{datetime.now().strftime('%Y%m%d')}",
                "generated_at":  datetime.now().isoformat(),
                "deviation_type": dt,
                "recurrence_count": count,
                "trigger_reason": tmpl["trigger"],
                "title":         tmpl["title"],
                "proposals":     tmpl["proposal"],
                "target_files":  tmpl["target_files"],
                "priority":      tmpl["priority"],
                "status":        "PENDING_APPROVAL",
                "approved_by":   None,
                "approved_at":   None,
                "seal_hash":     None,
            }
            candidates.append(candidate)
            print(f"\n  ✦ [{tmpl['priority'].upper()}] {tmpl['title']}")
            print(f"    トリガー: {tmpl['trigger']} ({count}件)")
            for p in tmpl["proposal"]:
                print(f"    → {p}")

    # Z軸低下による追加提案
    if z_alert:
        candidates.append({
            "id":            f"PC_Z_DRIFT_{datetime.now().strftime('%Y%m%d')}",
            "generated_at":  datetime.now().isoformat(),
            "deviation_type": "Z_AXIS_DRIFT",
            "recurrence_count": 0,
            "trigger_reason": f"Z軸制度整合性の継続的低下 (mean={z_mean}, {z_stab})",
            "title":         "制度整合性回復プログラム",
            "proposals":     [
                "recurrence_registryを週次で分析し制度改善を継続実施する",
                "Z軸が0.70を下回った場合は自動でWARNイベントを生成する",
                "OVERVIEW.jsonのcurrent_phaseにZ軸状態を反映する",
            ],
            "target_files":  ["data/recurrence_registry.csv", "MOCKA_OVERVIEW.json"],
            "priority":      "high",
            "status":        "PENDING_APPROVAL",
            "approved_by":   None,
            "approved_at":   None,
            "seal_hash":     None,
        })
        print(f"\n  ✦ [HIGH] 制度整合性回復プログラム")
        print(f"    トリガー: Z軸低下 (mean={z_mean})")

    # Human Gate
    print(f"\n{'='*55}")
    print(f"HUMAN GATE — きむら博士の承認待ち")
    print(f"{'='*55}")
    print(f"制度改善候補: {len(candidates)}件")
    print(f"承認後に mocka-seal で封印してください。")
    print(f"\n承認コマンド例:")
    for c in candidates:
        print(f"  python interface/policy_generator.py --approve {c['id']}")

    # policy_candidates.json に保存
    with open(POLICY_CANDIDATES, "w", encoding="utf-8") as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)

    print(f"\n出力: {POLICY_CANDIDATES}")
    print(f"Day4完了。Human Gateで承認を待ちます。")
    return candidates

def approve(policy_id: str):
    """承認処理"""
    if not POLICY_CANDIDATES.exists():
        print("ERROR: policy_candidates.json が見つかりません")
        return
    with open(POLICY_CANDIDATES, encoding="utf-8") as f:
        candidates = json.load(f)
    found = False
    for c in candidates:
        if c["id"] == policy_id:
            c["status"]      = "APPROVED"
            c["approved_by"] = "nsjp_kimura"
            c["approved_at"] = datetime.now().isoformat()
            found = True
            print(f"✓ 承認: {c['title']}")
            print(f"  mocka-seal で封印してください。")
    if not found:
        print(f"ERROR: {policy_id} が見つかりません")
    with open(POLICY_CANDIDATES, "w", encoding="utf-8") as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3 and sys.argv[1] == "--approve":
        approve(sys.argv[2])
    else:
        generate()
