"""Phase 8: Release Gate — final, all-AND enforcement before release.

No manual override and no bypass flag are accepted: `can_release` is a pure
function of the observed context.
"""

from __future__ import annotations

from scoring.prs_engine import PRODUCTION_ELIGIBLE_THRESHOLD

REQUIRED_CONTEXT_KEYS = (
    "deployment_certified",
    "sla_pass",
    "prs",
    "contract_valid",
    "observability_complete",
)


class ReleaseGate:
    def can_release(self, context: dict) -> bool:
        missing = [key for key in REQUIRED_CONTEXT_KEYS if key not in context]
        if missing:
            raise ValueError(f"release gate context missing required keys: {missing}")

        return all([
            context["deployment_certified"] is True,
            context["sla_pass"] is True,
            context["prs"] >= PRODUCTION_ELIGIBLE_THRESHOLD,
            context["contract_valid"] is True,
            context["observability_complete"] is True,
        ])
