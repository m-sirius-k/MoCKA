"""MoCKA Constitutional Runtime v1.0-stubs Trial.

Status: EXPERIMENTAL / ISOLATED / NOT CONNECTED TO PRODUCTION.

This package is a NEW MoCKA trial implementation. It is NOT a recovery,
reproduction, or reconstruction of any pre-existing "Constitutional Runtime
v1.0-stubs". The internals of any such pre-existing system are NOT OBSERVED
(see docs/audits/CONSTITUTIONAL_RUNTIME_V1_STUBS_WEB_EVIDENCE_RECOVERY_v0.1.md).

Everything defined here is DESIGNED for this trial, informed only by observed
behavioral boundaries reported from the 50-test experiment.

Isolation rules:
- No import of MoCKA production modules.
- No write to events.db, Decision Ledger, Human Gate, or any production store.
- Standard library only.
"""

__all__ = [
    "contract",
    "primitives",
    "runtime_basic",
    "runtime_extended",
    "gateway",
    "audit",
]

TRIAL_NAME = "MoCKA Constitutional Runtime v1.0-stubs Trial"
TRIAL_STATUS = "EXPERIMENTAL / ISOLATED"
