"""
MoCKA deviation_classifier.py
逸脱7分類エンジン + recurrence_registry 書き込み
Day2実装 - TODO_013
"""
import csv, json
from datetime import datetime
from pathlib import Path

BASE           = Path("C:/Users/sirok/MoCKA")
TRAJECTORY_CSV = BASE / "data/trajectory.csv"
RECURRENCE_CSV = BASE / "data/recurrence_registry.csv"

# 逸脱7分類の定義
DEVIATION_DEFS = {
    "FAST_WRONG":         "速く実行したが内容が誤り。event_idの採番ミス・誤ったファイル操作等",
    "SLOW_DRIFT":         "緩やかなズレ。指示から徐々に外れていく。複数セッションで顕在化",
    "FORMAT_COLLAPSE":    "フォーマット崩壊。event_idが_autoのままMCP経由で記録された等",
    "DEPENDENCY_BREAK":   "依存関係破壊。ledger/hashの不整合、SHA-256チェーン断絶",
    "INSTRUCTION_IGNORE": "指示無視。明示的な禁止事項（上書き禁止等）を破った",
    "SCOPE_CREEP":        "範囲逸脱。依頼されていないファイル・機能を勝手に変更",
    "PROTOCOL_SKIP":      "プロトコルスキップ。mocka_get_overview/get_todoを呼ばずに作業開始",
}

# 重大度マッピング
SEVERITY = {
    "INSTRUCTION_IGNORE": "critical",
    "DEPENDENCY_BREAK":   "high",
    "SCOPE_CREEP":        "high",
    "FORMAT_COLLAPSE":    "medium",
    "PROTOCOL_SKIP":      "medium",
    "FAST_WRONG":         "low",
    "SLOW_DRIFT":         "low",
}

# 警告閾値
WARN_THRESHOLD   = 3
POLICY_THRESHOLD = 5

RECURRENCE_HEADER = [
    "recorded_at", "event_id", "deviation_type", "severity",
    "who_actor", "what_type", "description",
    "recurrence_count", "warn_triggered", "policy_triggered"
]

def load_existing() -> dict:
    """既存のrecurrence_registryから累積カウントを読む"""
    counts = {}
    if not RECURRENCE_CSV.exists():
        return counts
    try:
        with open(RECURRENCE_CSV, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                dt = row.get("deviation_type","")
                if dt:
                    counts[dt] = counts.get(dt, 0) + 1
    except:
        pass
    return counts

def classify_from_trajectory():
    print("="*50)
    print("MoCKA deviation_classifier.py Day2")
    print("逸脱分類 + recurrence_registry 構築")
    print("="*50)

    if not TRAJECTORY_CSV.exists():
        print("ERROR: trajectory.csv が見つかりません。Day1を先に実行してください")
        return

    existing_counts = load_existing()
    new_violations  = []

    with open(TRAJECTORY_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("category") != "VIOLATION":
                continue
            dt       = row.get("deviation_type","")
            if not dt:
                continue

            # 累積カウント更新
            existing_counts[dt] = existing_counts.get(dt, 0) + 1
            count = existing_counts[dt]

            warn_triggered   = count >= WARN_THRESHOLD
            policy_triggered = count >= POLICY_THRESHOLD

            new_violations.append({
                "recorded_at":      datetime.now().isoformat(),
                "event_id":         row.get("event_id",""),
                "deviation_type":   dt,
                "severity":         SEVERITY.get(dt,"medium"),
                "who_actor":        row.get("who_actor",""),
                "what_type":        row.get("what_type",""),
                "description":      DEVIATION_DEFS.get(dt,""),
                "recurrence_count": count,
                "warn_triggered":   str(warn_triggered),
                "policy_triggered": str(policy_triggered),
            })

    # recurrence_registry に追記
    file_exists = RECURRENCE_CSV.exists()
    with open(RECURRENCE_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=RECURRENCE_HEADER)
        if not file_exists:
            w.writeheader()
        w.writerows(new_violations)

    # サマリー
    print(f"\n--- 逸脱分類結果 ---")
    print(f"VIOLATION件数: {len(new_violations)}")
    for dt, count in sorted(existing_counts.items(), key=lambda x: -x[1]):
        sev  = SEVERITY.get(dt,"?")
        warn = " ⚠ WARN"   if count >= WARN_THRESHOLD   else ""
        pol  = " 🔴 POLICY" if count >= POLICY_THRESHOLD else ""
        print(f"  {dt:<25} 累計{count:>3}件  [{sev}]{warn}{pol}")

    print(f"\n7分類定義:")
    for dt, desc in DEVIATION_DEFS.items():
        print(f"  {dt:<25} {desc[:40]}")

    print(f"\n出力: {RECURRENCE_CSV}")
    print("Day2完了。")

if __name__ == "__main__":
    classify_from_trajectory()
