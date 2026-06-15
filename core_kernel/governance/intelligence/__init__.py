"""Governance Intelligence Layer (Phase 7).

Sits above Self Verification (Phase 5) and Traceability (Phase 6).
Adds an *interpretation* layer that never changes Decision/Audit data,
only explains it:

  - drift_interpreter: gives each DriftFinding a meaning + severity +
    recommended action (interpretation, not detection).
  - decision_rationale: turns a DecisionRecord into a reasoned
    explanation object, citing the Validation/Compliance/Policy
    evidence that produced it.
  - requirement_history: an append-only, intent-tagged log of *why*
    Requirements changed (design intent), separate from the Audit
    trail (which records *what* happened at runtime).
  - intelligence_report: combines the above into one report.

Dependency direction: intelligence -> self_verification -> {contracts,
engines, runtime, audit}. Nothing below this layer imports it.
"""

from .decision_rationale import RationaleRecord, build_rationale
from .drift_interpreter import DriftSeverity, InterpretedDrift, interpret_drift
from .requirement_history import RequirementChange, RequirementHistoryStore
from .intelligence_report import IntelligenceReport, generate_intelligence_report

__all__ = [
    "RationaleRecord",
    "build_rationale",
    "DriftSeverity",
    "InterpretedDrift",
    "interpret_drift",
    "RequirementChange",
    "RequirementHistoryStore",
    "IntelligenceReport",
    "generate_intelligence_report",
]
