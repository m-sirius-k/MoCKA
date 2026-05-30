"""
vasAI Core: MoCKA Bridge — vasAI → MoCKA への還流ブリッジ。
OUTCOMEとWHY/REASONをMoCKAのessenceに自動還流する。
"""
import json
from datetime import datetime, timezone
from typing import Optional

from core import event_store


class MoCKABridge:
    """
    vasAI の PHI DNA を MoCKA PHILOSOPHY/OPERATION/INCIDENT 軸に還流する。
    MoCKAが利用可能でない場合も、還流ログをevent_storeに記録して継続。
    """

    def __init__(self, phi_layer=None):
        from core.phi_layer import PHILayer
        self._phi = phi_layer or PHILayer()

    def push_outcome_to_essence(self, dna_id: str) -> bool:
        """OUTCOMEをMoCKA OPERATION軸に還流。"""
        from core.phi_layer import initialize as phi_init, _get_conn as phi_conn
        phi_init()
        conn = phi_conn()
        row = conn.execute(
            "SELECT * FROM phi_dna WHERE dna_id=?", (dna_id,)
        ).fetchone()
        if row is None or not row["outcome"]:
            return False

        d = dict(row)
        event_store.append(
            who_actor="vasAI.mocka_bridge",
            what_type="ESSENCE_OPERATION_PUSH",
            where_component="mocka/essence/operation",
            why_purpose="PHI DNA OUTCOME → MoCKA OPERATION軸還流",
            content={
                "dna_id":     dna_id,
                "decision_id": d["decision_id"],
                "axis":       "OPERATION",
                "outcome":    d["outcome"],
                "outcome_at": d["outcome_at"],
            },
            stage="AUDIT",
        )
        return True

    def push_reasoning_to_essence(self, dna_id: str) -> bool:
        """WHY/REASONをMoCKA PHILOSOPHY軸に還流。"""
        from core.phi_layer import initialize as phi_init, _get_conn as phi_conn
        phi_init()
        conn = phi_conn()
        row = conn.execute(
            "SELECT * FROM phi_dna WHERE dna_id=?", (dna_id,)
        ).fetchone()
        if row is None:
            return False

        d = dict(row)
        event_store.append(
            who_actor="vasAI.mocka_bridge",
            what_type="ESSENCE_PHILOSOPHY_PUSH",
            where_component="mocka/essence/philosophy",
            why_purpose="PHI DNA WHY/REASON → MoCKA PHILOSOPHY軸還流",
            content={
                "dna_id":      dna_id,
                "decision_id": d["decision_id"],
                "axis":        "PHILOSOPHY",
                "why":         d["why"],
                "reason":      d["reason"],
            },
            stage="AUDIT",
        )
        return True

    def push_failure_to_incident(self, dna_id: str) -> bool:
        """失敗OUTCOMEをMoCKA INCIDENT軸に還流。"""
        from core.phi_layer import initialize as phi_init, _get_conn as phi_conn
        phi_init()
        conn = phi_conn()
        row = conn.execute(
            "SELECT * FROM phi_dna WHERE dna_id=?", (dna_id,)
        ).fetchone()
        if row is None or not row["outcome"]:
            return False

        d = dict(row)
        is_failure = "失敗" in d["outcome"] or "未達成" in d["outcome"]
        if not is_failure:
            return False

        event_store.append(
            who_actor="vasAI.mocka_bridge",
            what_type="ESSENCE_INCIDENT_PUSH",
            where_component="mocka/essence/incident",
            why_purpose="PHI DNA 失敗OUTCOME → MoCKA INCIDENT軸還流",
            content={
                "dna_id":        dna_id,
                "decision_id":   d["decision_id"],
                "axis":          "INCIDENT",
                "failure_detail": d["outcome"],
            },
            stage="INCIDENT",
        )
        return True

    def verify_sync(self) -> dict:
        """還流状態の確認（未還流件数・最終還流時刻）。"""
        from core.phi_layer import initialize as phi_init, _get_conn as phi_conn
        phi_init()
        conn = phi_conn()

        total = conn.execute("SELECT COUNT(*) as c FROM phi_dna").fetchone()["c"]
        exported = conn.execute(
            "SELECT COUNT(*) as c FROM phi_dna WHERE essence_exported=1"
        ).fetchone()["c"]
        pending = total - exported

        # 最終還流イベント確認
        essence_events = event_store.list_events(
            limit=1, what_type="ESSENCE_OPERATION_PUSH"
        )
        last_push_at = (
            essence_events[0]["when_ts"] if essence_events else None
        )

        return {
            "total_dna":      total,
            "exported":       exported,
            "pending":        pending,
            "last_push_at":   last_push_at,
            "sync_complete":  pending == 0,
        }

    def full_export(self, dna_id: str) -> dict:
        """PHILOSOPHY + OPERATION + INCIDENT の全軸を還流。"""
        results = {
            "dna_id":    dna_id,
            "philosophy": self.push_reasoning_to_essence(dna_id),
            "operation":  self.push_outcome_to_essence(dna_id),
            "incident":   self.push_failure_to_incident(dna_id),
        }
        # MoCKA essence形式エクスポートも実行
        essence = self._phi.export_to_essence(dna_id)
        results["essence"] = essence
        return results
