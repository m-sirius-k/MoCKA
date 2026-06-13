"""Phase 8: Deployment Certification.

Approves or rejects a deployment based on PRS, SLA, incident count,
telemetry completeness, and rollback plan presence. Integrates with
Phase 7 observability (event_stream_collector / telemetry_aggregator)
to enforce replay-ability and event-integrity checks.

No manual override, no bypass flags: `certify()` takes only observed
inputs and returns a deterministic APPROVED/REJECTED result.
"""

from __future__ import annotations

import hashlib
import os
import sys

# Allow importing Phase 7 observability modules from the sibling package.
_MOCKA_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_OBS_DIR = os.path.join(_MOCKA_ROOT, "production_observability")
for _path in (_MOCKA_ROOT, _OBS_DIR):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from event_stream_collector import EventStreamCollector  # noqa: E402

from certification.certificate_generator import DeploymentCertificate, generate_certificate
from scoring.prs_engine import PRODUCTION_ELIGIBLE_THRESHOLD


def compute_telemetry_snapshot_hash(collector: EventStreamCollector) -> str:
    """Hash the full replayable event stream. Used as a tamper/integrity check."""
    events = collector.replay()
    digest = hashlib.sha256()
    for event in events:
        digest.update(event.event_id.encode("utf-8"))
        digest.update(event.event_type.value.encode("utf-8"))
        digest.update(str(event.timestamp).encode("utf-8"))
    return digest.hexdigest()


def check_replayable(collector: EventStreamCollector) -> bool:
    """An empty stream is not replayable; a stream must be reconstructible
    from offset 0 without error."""
    try:
        events = collector.replay(since_index=0)
    except Exception:
        return False
    return len(events) > 0


class DeploymentCertifier:
    REQUIRED_CONTEXT_KEYS = (
        "prs_score",
        "sla_pass",
        "sla_score",
        "incident_count",
        "telemetry_complete",
        "rollback_plan_exists",
        "model_version_hash",
        "collector",
    )

    def certify(self, context: dict) -> DeploymentCertificate:
        missing = [key for key in self.REQUIRED_CONTEXT_KEYS if key not in context]
        if missing:
            raise ValueError(f"certification context missing required keys: {missing}")

        collector: EventStreamCollector = context["collector"]

        replayable = check_replayable(collector)
        telemetry_hash = compute_telemetry_snapshot_hash(collector)

        approved = all([
            context["prs_score"] >= PRODUCTION_ELIGIBLE_THRESHOLD,
            context["sla_pass"] is True,
            context["incident_count"] == 0,
            context["telemetry_complete"] is True,
            context["rollback_plan_exists"] is True,
            replayable,
        ])

        status = "APPROVED" if approved else "REJECTED"

        return generate_certificate(
            model_hash=context["model_version_hash"],
            telemetry_hash=telemetry_hash,
            sla_score=context["sla_score"],
            prs_score=context["prs_score"],
            status=status,
        )
