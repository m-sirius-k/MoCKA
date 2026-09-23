"""
MoCKA 3.0 — Memory Layer
memory_binding_trace.py

責務:
  Institutional Memory がDecisionにBINDされたことを追跡するモデル。

  - 記録された知識 (MemoryEntry) が
  - 後続のDecisionで実際に参照・検討されたこと
  を証明可能にする。

  RECORDED ≠ USED の区別を明確にし、
  各段階(RECORDED/RETRIEVED/PRESENTED/CONSIDERED/USED/INFLUENCED)を
  個別に記録・検証可能にする。

  本モデルは Decision Authorityを生成しない。
  Traceability only.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass(frozen=True)
class MemoryBindingTrace:
    """Memory-Decision間の関係性を記録するTrace。"""

    binding_id: str                    # BIND_<date>_<seq>
    knowledge_record_id: str           # memory_id (M_EPISODIC_000001等)
    retrieval_id: str                  # 取得操作のID (optional)
    decision_id: str                   # DC_<date>_<seq>
    binding_status: str                # RECORDED/RETRIEVED/PRESENTED/CONSIDERED
    authority_reference: Optional[str] = None  # HG decision if applicable
    scope_reference: Optional[str] = None      # STEP11_PHASE_A等
    evidence_reference: Optional[str] = None   # verification test ID等
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "binding_id": self.binding_id,
            "knowledge_record_id": self.knowledge_record_id,
            "retrieval_id": self.retrieval_id,
            "decision_id": self.decision_id,
            "binding_status": self.binding_status,
            "authority_reference": self.authority_reference,
            "scope_reference": self.scope_reference,
            "evidence_reference": self.evidence_reference,
            "timestamp": self.timestamp,
            "notes": self.notes,
        }

    @staticmethod
    def from_dict(data: dict) -> "MemoryBindingTrace":
        return MemoryBindingTrace(
            binding_id=data["binding_id"],
            knowledge_record_id=data["knowledge_record_id"],
            retrieval_id=data.get("retrieval_id", ""),
            decision_id=data["decision_id"],
            binding_status=data["binding_status"],
            authority_reference=data.get("authority_reference"),
            scope_reference=data.get("scope_reference"),
            evidence_reference=data.get("evidence_reference"),
            timestamp=data.get("timestamp", ""),
            notes=data.get("notes", ""),
        )
