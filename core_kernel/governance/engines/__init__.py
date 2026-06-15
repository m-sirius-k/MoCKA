"""Governance Engines layer.

Each engine is a pure function: Contract(s) in -> Contract/Result out.
No side effects other than logging. Engines depend only on
``core_kernel.governance.contracts`` — never on each other or on
``core_kernel.governance.runtime``.

Fixed flow (one-way):
    Validation Engine -> Compliance Engine -> Policy Engine -> Decision Engine
"""

from .validation_engine import run_validation
from .compliance_engine import run_compliance
from .policy_engine import run_policy
from .decision_engine import DecisionRecord, DecisionResult, run_decision

__all__ = [
    "run_validation",
    "run_compliance",
    "run_policy",
    "DecisionRecord",
    "DecisionResult",
    "run_decision",
]
