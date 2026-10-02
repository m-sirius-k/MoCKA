"""
aur/assessment.py: Assessment (A) — first condition of A-U-R theorem.

Contract: docs/contracts/assessment_contract_v1.md
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

CONFIDENCE_THRESHOLD = 0.5
ASSESSMENT_TTL_SECONDS = 300

REQUIRED_AXES = ("X", "Y", "Z", "T", "S", "K")


@dataclass
class AssessmentRecord:
    assessment_id: str
    action_id: str
    timestamp: str
    axes: dict
    admissible: bool
    reason: str
    confidence: float
    assessor: str
    scope: list = field(default_factory=list)
    constraints: dict = field(default_factory=dict)


def _generate_id() -> str:
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"ASSESS-{today}-{uuid.uuid4().hex[:8]}"


def _count_unknown_axes(axes: dict) -> int:
    return sum(1 for k in REQUIRED_AXES if axes.get(k) in (None, "UNKNOWN", ""))


def create_assessment(
    action_id: str,
    axes: dict,
    assessor: str = "system",
    scope: Optional[list] = None,
    constraints: Optional[dict] = None,
    reassessment_context=None,
) -> AssessmentRecord:
    """
    Create an AssessmentRecord for the given action.

    axes must contain keys X, Y, Z, T, S, K.
    Missing or UNKNOWN axes are allowed but reduce confidence.
    reassessment_context (ReassessmentContext) adjusts confidence if provided.
    """
    normalized_axes = {}
    for k in REQUIRED_AXES:
        v = axes.get(k)
        normalized_axes[k] = v if v not in (None, "") else "UNKNOWN"

    unknown_count = _count_unknown_axes(normalized_axes)
    base_confidence = 1.0 - (unknown_count * 0.15)

    confidence_adjustment = 0.0
    if reassessment_context is not None and reassessment_context.has_prior_data:
        confidence_adjustment = reassessment_context.confidence_adjustment

    confidence = max(0.0, min(1.0, base_confidence + confidence_adjustment))

    violations = []
    for k in REQUIRED_AXES:
        v = normalized_axes.get(k, "UNKNOWN")
        if isinstance(v, str) and v.upper() in ("VIOLATION", "FORBIDDEN", "BLOCKED"):
            violations.append(k)

    if violations:
        admissible = False
        reason = f"axis violations detected: {violations}"
    elif confidence < CONFIDENCE_THRESHOLD:
        admissible = False
        reason = f"confidence {confidence:.2f} below threshold {CONFIDENCE_THRESHOLD}"
    else:
        admissible = True
        reason = "all axes evaluated, confidence acceptable"
        if unknown_count > 0:
            reason += f" ({unknown_count} axes UNKNOWN)"

    warnings = []
    if reassessment_context is not None and reassessment_context.warnings:
        warnings = reassessment_context.warnings
        if warnings:
            reason += f"; prior warnings: {warnings[:2]}"

    return AssessmentRecord(
        assessment_id=_generate_id(),
        action_id=action_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        axes=normalized_axes,
        admissible=admissible,
        reason=reason,
        confidence=confidence,
        assessor=assessor,
        scope=scope or [],
        constraints=constraints or {},
    )


def is_assessment_fresh(record: AssessmentRecord) -> bool:
    """Return True if the assessment is within TTL."""
    try:
        created = datetime.fromisoformat(record.timestamp)
        now = datetime.now(timezone.utc)
        elapsed = (now - created).total_seconds()
        return elapsed <= ASSESSMENT_TTL_SECONDS
    except Exception:
        return False
