# phi_os/migrate_prevention_queue.py
# Phase3移行スクリプト: data/prevention_queue.json -> phi_os.human_gate event
#
# 方針(確定): 状態復元ではなくイベント再生成。
#   status="NEW"   -> submit(PENDING)として正規化(全1769件相当)
#   status="approved" -> submit + approve(疑似遷移として補完。元のPENDING履行
#                          は記録されていないため、移行時刻でsubmitしてから
#                          即approveする2イベントとして再構成する)
#   status="PENDING"(GL7仕様通りの大文字) -> 0件想定だが将来発生時はsubmitのみ
#   status="rejected" -> submit + reject(同様に疑似遷移)
# 冪等性: request_id(=元のid)で既存eventがあればスキップする(hg.get_state()で判定)。
# prevention_queue.json自体は読み取りのみで、本スクリプトは変更しない(廃止はPhase3の別ステップ)。
import sys
import json
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from phi_os import human_gate as hg

QUEUE_PATH = _REPO_ROOT / "data" / "prevention_queue.json"


def _normalize_status(raw_status: str) -> str:
    s = (raw_status or "").strip()
    if s in ("NEW", "PENDING", "pending"):
        return "PENDING"
    if s == "approved":
        return "APPROVED"
    if s == "rejected":
        return "REJECTED"
    return "UNKNOWN"


def migrate(dry_run: bool = True) -> dict:
    data = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    queue = data.get("queue", [])

    summary = {"total": len(queue), "migrated": 0, "skipped_existing": 0, "skipped_unknown_status": 0, "errors": []}

    for item in queue:
        request_id = item.get("id", "")
        if not request_id:
            summary["errors"].append({"item": item, "error": "missing id"})
            continue

        target = _normalize_status(item.get("status", ""))
        if target == "UNKNOWN":
            summary["skipped_unknown_status"] += 1
            continue

        if hg.get_state(request_id) is not None:
            summary["skipped_existing"] += 1
            continue

        if dry_run:
            summary["migrated"] += 1
            continue

        payload = {
            "request_id": request_id,
            "source": "prevention_queue_migration",
            "original_status": item.get("status", ""),
            "recurrence_key": item.get("recurrence_key", ""),
            "component": item.get("component", ""),
            "what_type": item.get("what_type", ""),
            "severity": item.get("severity", ""),
        }
        hg.submit(payload)
        if target == "APPROVED":
            hg.approve(request_id, {"note": "pseudo-transition from migration, no original PENDING history"})
        elif target == "REJECTED":
            hg.reject(request_id, {"note": "pseudo-transition from migration, no original PENDING history"})
        summary["migrated"] += 1

    return summary


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="指定しない場合はdry-run(件数集計のみ、書き込みなし)")
    args = parser.parse_args()
    result = migrate(dry_run=not args.apply)
    print(json.dumps(result, ensure_ascii=False, indent=2))
