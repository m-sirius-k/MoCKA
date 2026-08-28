"""MoCKA Constitutional Runtime v1.0-stubs Trial-Basic.

Status: DESIGNED (this trial). Not a recovery of any pre-existing runtime.

Scope: the smallest deterministic structure that can answer
"what does the CR receive, what does it judge, and when does it stop execution".

Design choices specific to Basic (all DESIGNED, all disclosed):

1. Short-circuit evaluation. The first rule that fires decides. This keeps the
   audit record to one primitive per decision. Trial-Extended collects all
   findings instead.
2. Collapsed vocabulary. Basic keeps the six-primitive set. Anything the
   extended vocabulary would split is folded:
     - authority_state in {LOST, REVOKED, MISMATCH} -> AUTHORITY_LOST
     - binding_status  in {MISSING, INVALID, UNMAPPED} -> CONTRACT_INVALID
     - every intake defect -> CONTRACT_INVALID
   The fold is lossy on purpose: Basic is the foundation, not the boundary
   stress test.
3. The witness rule is an explicit policy, per the specification. The default
   is UNKNOWN (not silent pass, not hard block), because Basic has no evidence
   primitive of its own.
4. A bound RE verdict may lower the decision, never raise it (see gateway).
"""

from datetime import datetime, timezone

from . import contract as contract_mod
from .gateway import apply_bound_verdict, gate
from .primitives import Category, Decision, Finding, Severity

WITNESS_POLICY_UNKNOWN = "UNKNOWN"
WITNESS_POLICY_BLOCK = "BLOCK"

TIER = "basic"
RUNTIME_NAME = "MoCKA Constitutional Runtime v1.0-stubs Trial-Basic"


class BasicPolicy(object):
    """Explicit, inspectable policy. No implicit defaults inside the rules."""

    __slots__ = ("witness_required", "witness_absent_policy")

    def __init__(self, witness_required=True, witness_absent_policy=WITNESS_POLICY_UNKNOWN):
        self.witness_required = witness_required
        self.witness_absent_policy = witness_absent_policy

    def as_dict(self):
        return {
            "witness_required": self.witness_required,
            "witness_absent_policy": self.witness_absent_policy,
        }


class Evaluation(object):
    __slots__ = (
        "runtime",
        "decision",
        "execution",
        "findings",
        "reason",
        "intake",
        "bound_verdict",
        "policy",
    )

    def __init__(self, runtime, decision, execution, findings, reason, intake, bound_verdict, policy):
        self.runtime = runtime
        self.decision = decision
        self.execution = execution
        self.findings = findings
        self.reason = reason
        self.intake = intake
        self.bound_verdict = bound_verdict
        self.policy = policy

    @property
    def primitives(self):
        return [f.primitive for f in self.findings]

    def as_dict(self):
        return {
            "runtime": self.runtime,
            "decision": self.decision.value,
            "execution": self.execution.value,
            "primitives": self.primitives,
            "findings": [f.as_dict() for f in self.findings],
            "bound_verdict": self.bound_verdict,
            "reason": self.reason,
            "policy": self.policy,
            "contract": self.intake.as_dict() if self.intake else None,
        }


def _now(now):
    if now is None:
        return datetime.now(timezone.utc)
    return now


def _finding(primitive, severity, category, field, detail):
    return Finding(primitive, severity, category, field, detail)


class ConstitutionalRuntimeBasic(object):
    """Stateless. One contract in, one decision out."""

    def __init__(self, policy=None):
        self.policy = policy or BasicPolicy()

    # -- rule chain --------------------------------------------------------

    def evaluate(self, raw_contract, now=None):
        now = _now(now)
        result = contract_mod.intake(raw_contract, require_decision_fields=True)

        # Rule 1: contract must survive typed intake.
        if not result.ok:
            first = result.defects[0]
            detail = "%s%s: %s" % (
                first.code,
                "" if first.field is None else "(%s)" % first.field,
                first.detail,
            )
            return self._stop(
                result,
                _finding("CONTRACT_INVALID", Severity.BLOCKING, Category.CONTRACT, first.field, detail),
                "contract failed typed intake; %d defect(s)" % len(result.defects),
            )

        c = result.contract

        # Rule 2: authority.
        if c.get("authority_state") != "VALID":
            return self._stop(
                result,
                _finding(
                    "AUTHORITY_LOST",
                    Severity.BLOCKING,
                    Category.AUTHORITY,
                    "authority_state",
                    "authority_state=%s (Basic collapses LOST/REVOKED/MISMATCH)" % c.get("authority_state"),
                ),
                "authority is not valid",
            )

        # Rule 3: admissibility false.
        if c.get("admissibility_state") == "INADMISSIBLE":
            return self._stop(
                result,
                _finding(
                    "INADMISSIBLE",
                    Severity.BLOCKING,
                    Category.ADMISSIBILITY,
                    "admissibility_state",
                    "admissible = false",
                ),
                "request is inadmissible",
            )

        # Rule 4: expiry.
        expires = contract_mod.timestamp(c, "expires_at")
        if expires is not None and expires <= now:
            return self._stop(
                result,
                _finding(
                    "EXPIRED",
                    Severity.BLOCKING,
                    Category.TEMPORAL,
                    "expires_at",
                    "expires_at=%s <= now=%s" % (expires.isoformat(), now.isoformat()),
                ),
                "contract expired",
            )

        # Rule 5: integrity.
        if c.get("integrity_status") != "VERIFIED":
            return self._stop(
                result,
                _finding(
                    "INTEGRITY_FAILURE",
                    Severity.BLOCKING,
                    Category.INTEGRITY,
                    "integrity_status",
                    "integrity_status=%s" % c.get("integrity_status"),
                ),
                "integrity not verified",
            )

        # Rule 6: binding. DESIGNED addition to the specification rule chain,
        # required so that an unbound RE verdict cannot reach the decision.
        if c.get("binding_status") != "BOUND":
            return self._stop(
                result,
                _finding(
                    "CONTRACT_INVALID",
                    Severity.BLOCKING,
                    Category.BINDING,
                    "binding_status",
                    "binding_status=%s; verdict is not bound to a typed decision"
                    % c.get("binding_status"),
                ),
                "verdict is not bound; Basic folds binding failure into CONTRACT_INVALID",
            )

        # Rule 7: witness, per explicit policy.
        witness_ok = bool(c.get("witness_present")) and c.get("witness_status") == "VALID"
        if self.policy.witness_required and not witness_ok:
            if self.policy.witness_absent_policy == WITNESS_POLICY_BLOCK:
                return self._stop(
                    result,
                    _finding(
                        "CONTRACT_INVALID",
                        Severity.BLOCKING,
                        Category.EVIDENCE,
                        "witness_present",
                        "required witness absent or invalid; policy=BLOCK",
                    ),
                    "required witness absent; policy BLOCK",
                )
            return self._stop(
                result,
                _finding(
                    "UNKNOWN",
                    Severity.INDETERMINATE,
                    Category.EVIDENCE,
                    "witness_present",
                    "required witness absent or invalid; policy=UNKNOWN",
                ),
                "required witness absent; policy UNKNOWN",
            )

        # Rule 8: any declared unknown state stays unknown.
        if c.get("admissibility_state") == "UNKNOWN":
            return self._stop(
                result,
                _finding(
                    "UNKNOWN",
                    Severity.INDETERMINATE,
                    Category.ADMISSIBILITY,
                    "admissibility_state",
                    "admissibility_state=UNKNOWN; never converted to ALLOW",
                ),
                "admissibility unknown",
            )

        # Rule 9: the bound verdict may lower the decision, never raise it.
        bound_verdict = c.get("re_verdict")
        decision = apply_bound_verdict(Decision.ALLOW, bound_verdict)
        if decision is Decision.ALLOW:
            reason = "all typed checks passed and bound verdict is ALLOW"
        else:
            reason = "bound RE verdict %s honored as a denial" % bound_verdict
        return Evaluation(
            RUNTIME_NAME,
            decision,
            gate(decision),
            [],
            reason,
            result,
            bound_verdict,
            self.policy.as_dict(),
        )

    # -- helper ------------------------------------------------------------

    def _stop(self, result, finding, reason):
        decision = Decision.BLOCK if finding.severity is Severity.BLOCKING else Decision.UNKNOWN
        return Evaluation(
            RUNTIME_NAME,
            decision,
            gate(decision),
            [finding],
            reason,
            result,
            None,
            self.policy.as_dict(),
        )
