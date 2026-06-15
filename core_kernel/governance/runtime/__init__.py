"""Governance Runtime layer.

Orchestration and flow control only. Runtime never re-evaluates,
scores, or re-interprets — it calls Engines in the fixed order and
acts solely on the resulting DecisionRecord.

    Event -> Validation -> Compliance -> Policy -> Decision
           -> Runtime Execution -> Commit -> Audit Log
"""

from .event_pipeline import GovernanceEvent, PipelineResult, run_pipeline
from .governance_runtime import AuditSink, CommitRecord, ExecutionResult, GovernanceRuntime

__all__ = [
    "GovernanceEvent",
    "PipelineResult",
    "run_pipeline",
    "AuditSink",
    "CommitRecord",
    "ExecutionResult",
    "GovernanceRuntime",
]
