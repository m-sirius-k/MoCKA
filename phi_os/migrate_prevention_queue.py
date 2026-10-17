# phi_os/migrate_prevention_queue.py
# Phase3移行スクリプト: data/prevention_queue.json -> phi_os.human_gate event
#
# 方針(A案・確定): 移行は全て PENDING での起票(submit)のみ。
#   approve / reject は一切呼ばない。人間の判断(Human Gate)を迂回する裏口を作らない。
#   元の status(NEW / approved / rejected 等)は payload の original_status に記録するだけで、
#   状態としては採用しない。approved / rejected の項目は legacy_decision として記録し、
#   MIGRATION_UNVERIFIED(根拠未検証)のフラグを付け、正式な承認フローで再審査する。
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

        # 移行は PENDING で起票するだけ。approve / reject は呼ばない（A案）。
        legacy = target in ("APPROVED", "REJECTED")
        payload = {
            "request_id": request_id,
            "source": "prevention_queue_migration",
            "original_status": item.get("status", ""),
            "recurrence_key": item.get("recurrence_key", ""),
            "component": item.get("component", ""),
            "what_type": item.get("what_type", ""),
            "severity": item.get("severity", ""),
            "migration_flag": "MIGRATION_UNVERIFIED" if legacy else None,
            "legacy_decision": target if legacy else None,
        }
        hg.submit(payload)
        if legacy:
            summary["legacy_decisions_quarantined"] = summary.get("legacy_decisions_quarantined", 0) + 1
        summary["migrated"] += 1

    return summary


PSEUDO_NOTE = "pseudo-transition from migration"


def find_legacy_pseudo_transitions(conn=None) -> list:
    """既に移行で書かれた擬似遷移（approve/reject）を一覧する。読み取りのみ・状態は変えない。
    戻り値は隔離（MIGRATION_UNVERIFIED）の対象。再審査は正式な承認フローで行う。"""
    owns = conn is None
    if owns:
        conn = hg._get_conn()
    try:
        hg._ensure_table(conn)
        rows = conn.execute(
            "SELECT event_id, timestamp, action, request_id, payload FROM human_gate_events "
            "WHERE payload LIKE ? ORDER BY timestamp ASC",
            ("%" + PSEUDO_NOTE + "%",),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        if owns:
            conn.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="指定しない場合はdry-run(件数集計のみ、書き込みなし)")
    args = parser.parse_args()
    result = migrate(dry_run=not args.apply)
    print(json.dumps(result, ensure_ascii=False, indent=2))
