from dataclasses import dataclass
from datetime import datetime, timezone
import uuid

from .institution_runtime import InstitutionRuntime
from .runtime_types import GateId


@dataclass(frozen=True)
class ObservationRecord:
    incident_id: str
    state: str
    evidence_reference: str
    timestamp: str


class ProductionObservation:

    def __init__(self):
        self.runtime = InstitutionRuntime.get_instance()

    def create_incident(self, evidence_reference: str) -> ObservationRecord:
        return ObservationRecord(
            incident_id=f"INC_{uuid.uuid4()}",
            state="HALTED",
            evidence_reference=evidence_reference,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    def verify_resume_authority(self, decision_record: dict) -> bool:
        required = [
            "gate_id",
            "approved",
        ]

        if not all(key in decision_record for key in required):
            return False

        if decision_record["approved"] is not True:
            return False

        try:
            gate_id = GateId(decision_record["gate_id"])
            authority = self.runtime.resolve_authority_for_gate(gate_id)

            return authority is not None

        except Exception:
            return False
