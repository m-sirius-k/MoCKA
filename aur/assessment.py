"""
aur/assessment.py: Assessment (A) — first condition of A-U-R theorem.

Contract: docs/contracts/assessment_contract_v1.md

Admissibility is comprehensive contract-based judgment:
  Evidence + Observation Context + Interpretation Separation
  + Freshness/Validity + Uncertainty + Impact
  + UNKNOWN conditions + contract-specific conditions
      -> admissible (True/False)
      -> confidence = auxiliary value expressing result uncertainty

UNKNOWN != FALSE: UNKNOWN on an axis reduces confidence but does NOT
automatically make the assessment inadmissible.
UNKNOWN != auto-ALLOW: UNKNOWN does not grant admissibility either.
confidence >= threshold alone does NOT make admissible.
confidence < threshold CAN make inadmissible (auxiliary fail-closed gate).
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

CONFIDENCE_THRESHOLD = 0.5
ASSESSMENT_TTL_SECONDS = 300

REQUIRED_AXES = ("X", "Y", "Z", "T", "S", "K")

_FRESHNESS_EXPIRED_MARKERS = ("expired", "stale", "invalid", "outdated", "revoked")
_VIOLATION_MARKERS = ("VIOLATION", "FORBIDDEN", "BLOCKED")


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
    return sum(1 for k in REQUIRED_AXES if axes.get(k) == "UNKNOWN")


def _evaluate_admissibility(original_axes: dict, normalized_axes: dict, confidence: float) -> tuple:
    """
    Comprehensive admissibility evaluation.

    Returns (admissible: bool, reason: str).

    Rules applied in order (any failure -> inadmissible):
    1. Violation in any axis value -> inadmissible
    2. X (Evidence) originally absent (None/"") -> inadmissible
       UNKNOWN is not absent: UNKNOWN reduces confidence only
    3. T (Freshness) explicitly expired/stale -> inadmissible
       UNKNOWN freshness reduces confidence only
    4. Y (Interpretation) identical to X (both non-UNKNOWN, non-empty) -> inadmissible
       (interpretation must be separated from evidence)
    5. confidence < CONFIDENCE_THRESHOLD -> inadmissible (auxiliary gate)
    6. All conditions satisfied -> admissible
    """
    # Rule 1: violation in any axis
    violations = [
        k for k in REQUIRED_AXES
        if isinstance(normalized_axes.get(k), str)
        and normalized_axes[k].upper() in _VIOLATION_MARKERS
    ]
    if violations:
        return False, f"axis violations detected: {violations}"

    # Rule 2: X (Evidence) absent — None or "" before normalization means no evidence gathered
    x_original = original_axes.get("X")
    if x_original in (None, ""):
        return False, "Evidence (X axis) absent: evidence must be gathered before assessment"

    # Rule 3: T (Freshness) explicitly expired
    t_value = normalized_axes.get("T", "UNKNOWN")
    if t_value != "UNKNOWN" and isinstance(t_value, str):
        t_lower = t_value.lower()
        if any(marker in t_lower for marker in _FRESHNESS_EXPIRED_MARKERS):
            return False, f"Freshness (T axis) expired or invalid: {t_value}"

    # Rule 4: Y (Interpretation) not separated from X
    x_val = normalized_axes.get("X", "UNKNOWN")
    y_val = normalized_axes.get("Y", "UNKNOWN")
    if (
        x_val != "UNKNOWN"
        and y_val != "UNKNOWN"
        and x_val == y_val
    ):
        return False, (
            f"Interpretation (Y axis) not separated from Evidence (X axis): "
            f"both are '{x_val}'"
        )

    # Rule 5: confidence auxiliary gate
    if confidence < CONFIDENCE_THRESHOLD:
        return False, f"confidence {confidence:.2f} below threshold {CONFIDENCE_THRESHOLD}"

    # Rule 6: all conditions passed
    unknown_count = _count_unknown_axes(normalized_axes)
    reason = "all admissibility conditions satisfied"
    if unknown_count > 0:
        reason += f" ({unknown_count} axes UNKNOWN, confidence adjusted)"
    return True, reason


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
    UNKNOWN on an axis != False. UNKNOWN != auto-admissible.
    Evidence (X) must be present (None/"" -> inadmissible regardless of confidence).
    Freshness (T) must not be expired.
    Interpretation (Y) must be separated from Evidence (X).
    reassessment_context (ReassessmentContext) adjusts confidence if provided.
    """
    original_axes = dict(axes)

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

    admissible, reason = _evaluate_admissibility(original_axes, normalized_axes, confidence)

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
