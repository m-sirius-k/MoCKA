from dataclasses import dataclass, asdict

@dataclass
class StateVector:
    goal_type: str
    uncertainty: float
    risk_level: float
    time_pressure: float
    abstraction_level: float
    novelty: float
    output_format: list
    evidence_required: float
    reversibility_required: float
    stakes: str

def build_state_vector(payload: dict) -> StateVector:
    return StateVector(
        goal_type=payload.get("goal_type", "analysis"),
        uncertainty=float(payload.get("uncertainty", 0.5)),
        risk_level=float(payload.get("risk_level", 0.3)),
        time_pressure=float(payload.get("time_pressure", 0.3)),
        abstraction_level=float(payload.get("abstraction_level", 0.5)),
        novelty=float(payload.get("novelty", 0.4)),
        output_format=payload.get("output_format", ["text"]),
        evidence_required=float(payload.get("evidence_required", 0.5)),
        reversibility_required=float(payload.get("reversibility_required", 0.5)),
        stakes=payload.get("stakes", "medium"),
    )