"""
Restore Materialization(Phase8-3)

validator.build_draft_restore_packet() が組み立てる in-memory ドラフトを、
再現可能な永続Artifactとして governance/write_path/restore/materialized/ (新規namespace)
へ書き込む。PlanningCaliber/fp/restore_packet.json(Legacy)へは一切書き込まない。

Adapter契約:
    本モジュールは validator.py / generator.py / adapter.py の公開関数のみを呼び出し、
    Runtime Binding Layer自体には一切手を加えない。

Supersede Chain Resolution(HG-WP-05確定):
    「最新」判定は 単純timestamp最大ではなく、
    Governance Seal一致 + sequence最大 + supersedes chain有効 の複合条件とする。
"""

import json
import sys
from pathlib import Path

MOCKA_ROOT = Path(r"C:\Users\sirok\MoCKA")
MATERIALIZED_DIR = MOCKA_ROOT / "governance" / "write_path" / "restore" / "materialized"

sys.path.insert(0, str(MOCKA_ROOT))
from governance.write_path.runtime import validator, generator, adapter  # noqa: E402


def _existing_packets() -> list:
    """materialized/配下の既存Artifactを全て読み込む(読み取り専用)。"""
    if not MATERIALIZED_DIR.exists():
        return []
    packets = []
    for f in sorted(MATERIALIZED_DIR.glob("RP_*.json")):
        try:
            packets.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            continue
    return packets


def _resolve_supersede_chain(current_anchor_hash: str):
    """
    HG-WP-05: Governance Seal一致 + sequence最大 + supersedes chain有効 の複合条件で
    「直前の有効な最新packet」を解決する。該当なしの場合は (None, 0) を返す。
    """
    candidates = [
        p for p in _existing_packets()
        if p.get("governance_anchor_hash") == current_anchor_hash
    ]
    if not candidates:
        return None, 0

    # supersedes chainの妥当性確認: 自身のsupersedesが存在するpacket_id、
    # またはNone(初代)であることを要求する
    known_ids = {p["packet_id"] for p in candidates}
    valid = [
        p for p in candidates
        if p.get("supersedes") is None or p.get("supersedes") in known_ids
    ]
    if not valid:
        return None, 0

    latest = max(valid, key=lambda p: p.get("sequence", 0))
    return latest["packet_id"], latest.get("sequence", 0)


def materialize(decision_id: str, generated_by: str) -> dict:
    """
    Restore Packet v1 を実際に永続化する(Materialization Event)。
    supersedes/sequenceは _resolve_supersede_chain() により自動決定する
    (呼び出し側からの手入力は受け付けない)。
    """
    draft = validator.build_draft_restore_packet(decision_id=decision_id, generated_by=generated_by)
    packet = draft["packet"]

    current_anchor = adapter._resolve_anchor_reference()
    supersedes_id, prev_sequence = _resolve_supersede_chain(current_anchor)

    MATERIALIZED_DIR.mkdir(parents=True, exist_ok=True)
    next_seq = prev_sequence + 1
    permanent_id = f"RP_{decision_id.replace('-', '')}_{next_seq:03d}"

    packet["packet_id"] = permanent_id
    packet["supersedes"] = supersedes_id
    packet["sequence"] = next_seq

    out_path = MATERIALIZED_DIR / f"{permanent_id}.json"
    if out_path.exists():
        raise FileExistsError(f"materialized packet already exists (append-only violation): {out_path}")
    out_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")

    change_result = generator.record_change_event(
        event_type="RESTORE_MATERIALIZED",
        record_id=permanent_id,
        extra=f"Write Path v1.0 Phase8-3: {permanent_id} materialized "
              f"(supersedes={supersedes_id}, sequence={next_seq})",
    )

    return {
        "packet_id": permanent_id,
        "path": str(out_path),
        "supersedes": supersedes_id,
        "sequence": next_seq,
        "change_event": change_result,
    }
