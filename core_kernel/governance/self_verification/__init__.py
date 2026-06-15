"""Self Verification layer.

Meta-layer that checks the chain

    Design -> Contract -> Implementation -> Unit Test
           -> Integration Test -> Evidence -> Audit Report

is consistent for each Requirement. This is NOT a test runner that
judges pass/fail quality; it verifies that every layer that *should*
exist for a given requirement *does* exist and is wired together, and
that the recorded Evidence matches what the Engines/Runtime/Audit
actually produce when executed.
"""

from .evidence import EvidenceBundle, collect_evidence
from .requirement_map import REQUIREMENTS, Requirement
from .verification_engine import SelfVerificationEngine, VerificationReport, VerificationStatus
from .audit_report import generate_audit_report

__all__ = [
    "EvidenceBundle",
    "collect_evidence",
    "REQUIREMENTS",
    "Requirement",
    "SelfVerificationEngine",
    "VerificationReport",
    "VerificationStatus",
    "generate_audit_report",
]
