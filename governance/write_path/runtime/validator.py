"""
Runtime Binding Layer オーケストレーション(Phase8-2)

generator.py(events.db -> RuntimeEvidenceRecord) と
adapter.py(decision_ledger.jsonl + anchor_record.json -> GovernanceTransitionRecord)
を束ね、RestorePacketV1のドラフトを組み立てて検証する。

本モジュールはPlanningCaliber/fp/restore_packet.jsonを一切開かない
(Legacy read-only維持。Phase8-2はLegacyへの参照すら持たない設計とすることで、
移行前後の依存を完全に分離する)。

ここで組み立てたRestorePacketV1ドラフトは in-memory のみであり、
どこにも永続化しない(Materialization = 実際の永続化はPhase8-2の対象外)。
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

MOCKA_ROOT = Path(r"C:\Users\sirok\MoCKA")
sys.path.insert(0, str(MOCKA_ROOT))

from governance.write_path.runtime import generator, adapter  # noqa: E402
from governance.write_path.restore import schema as restore_schema  # noqa: E402


def build_draft_restore_packet(decision_id: str, generated_by: str) -> dict:
    """
    Evidence Record + Transition Record を束ねて RestorePacketV1 ドラフトを組み立てる。
    governance_anchor_hash は Transition Record の anchor_reference を継承する
    (Restore AuthorityはGovernance Sealのみ、DC-WP-001準拠)。
    """
    evidence = generator.generate_evidence_record(generated_by=generated_by)
    transition = adapter.build_transition_record(decision_id=decision_id)

    # Evidence Record自体にも、生成時点で有効だったGovernance Seal値を埋め戻す
    evidence["governance_anchor_hash"] = transition["anchor_reference"]

    payload = {
        "immutable": {"philosophy": [], "forbidden": [], "values": []},
        "restore_5points": {},
        "session_context": f"write_path_v1 phase8-2 draft ({decision_id})",
    }
    content_hash = hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()

    packet = {
        "schema_version": "1.0",
        "packet_id": f"RP_DRAFT_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "governance_anchor_hash": transition["anchor_reference"],
        "runtime_evidence_ref": evidence["record_id"],
        "decision_refs": [transition["governance_transition_id"]],
        "event_range": evidence["source_event_range"],
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "content_hash": content_hash,
        "immutable": True,
        "supersedes": None,
        "sequence": 1,
        "payload": payload,
    }

    errors = restore_schema.validate(packet)
    if errors:
        raise ValueError(f"draft RestorePacketV1 failed validation: {errors}")

    return {"evidence": evidence, "transition": transition, "packet": packet}


def check_freshness_against_current_anchor(packet: dict) -> bool:
    """draft packetのgovernance_anchor_hashを、現在のanchor_record.jsonと突合する。"""
    current = adapter._resolve_anchor_reference()
    return restore_schema.is_fresh(packet, current)
