"""MoCKA Constitutional Runtime v1.0-stubs Trial-Extended.

Status: DESIGNED (this trial). Not a recovery of any pre-existing runtime.

Scope: boundary stress. Where Trial-Basic asks "is this contract usable",
Trial-Extended asks "how does this contract fail, and can any failure mode
reach ALLOW".

Design choices specific to Extended (all DESIGNED, all disclosed):

1. Collect-all evaluation. Every category is evaluated and every finding is
   recorded, then the decision is reduced once. Basic short-circuits; Extended
   does not, because the audit value is in the full failure set.
2. Split vocabulary. What Basic folds, Extended separates
   (AUTHORITY_LOST / REVOKED / MISMATCH, BINDING_MISSING / INVALID / UNMAPPED,
   CONTRACT_MISSING / UNPARSABLE / SCHEMA_MISMATCH / VERSION_DRIFT).
3. Two-speed contract failure. Missing METADATA is a schema mismatch and
   blocks. Missing DECISION-BEARING fields is CONTRACT_SEMANTICALLY_INCOMPLETE
   and yields UNKNOWN. A well-formed envelope with nothing decidable inside is
   not the same defect as a malformed envelope, and neither is an ALLOW.
4. Statefulness. Replay and monotonic-time checks need memory, so this runtime
   keeps a nonce ledger, a request ledger, and a per-subject high-water mark.
5. Signatures are recomputed, never trusted as a claim. A contract that says it
   is signed but carries no signature field raises SIGNATURE_MISSING.

The prose quarantine is never read. No primitive in this module is produced by
matching text.
"""

import hashlib
import hmac
import json
from datetime import datetime, timezone

from . import contract as contract_mod
from .gateway import apply_bound_verdict, gate
from .primitives import (
    Category,
    Decision,
    Finding,
    Severity,
    category_of,
    decide,
    is_known,
    severity_of,
)

TIER = "extended"
RUNTIME_NAME = "MoCKA Constitutional Runtime v1.0-stubs Trial-Extended"

# Trial-local signing key. Isolated: no production key material is used.
TRIAL_SIGNING_KEY = b"mocka-cr-trial-v1.0-stubs-local-key"

_SIGNATURE_EXCLUDED = ("signature", "verdict_digest", "payload_digest")


def canonical_payload(typed):
    """Deterministic serialization of the typed fields that are signed."""
    body = {k: v for k, v in typed.items() if k not in _SIGNATURE_EXCLUDED}
    return json.dumps(body, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def sign(typed, key=TRIAL_SIGNING_KEY):
    return hmac.new(key, canonical_payload(typed), hashlib.sha256).hexdigest()


def verdict_digest(verdict):
    return hashlib.sha256(("verdict:%s" % verdict).encode("utf-8")).hexdigest()


class ExtendedPolicy(object):
    __slots__ = ("witness_required", "signature_required", "nonce_required", "clock_skew_seconds")

    def __init__(
        self,
        witness_required=True,
        signature_required=True,
        nonce_required=True,
        clock_skew_seconds=0,
    ):
        self.witness_required = witness_required
        self.signature_required = signature_required
        self.nonce_required = nonce_required
        self.clock_skew_seconds = clock_skew_seconds

    def as_dict(self):
        return {
            "witness_required": self.witness_required,
            "signature_required": self.signature_required,
            "nonce_required": self.nonce_required,
            "clock_skew_seconds": self.clock_skew_seconds,
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


def _f(primitive, field, detail):
    """Build a Finding, taking severity and category from the registry."""
    return Finding(primitive, severity_of(primitive), category_of(primitive), field, detail)


class ConstitutionalRuntimeExtended(object):
    def __init__(self, policy=None):
        self.policy = policy or ExtendedPolicy()
        self.reset()

    def reset(self):
        self._nonces = set()
        self._requests = set()
        self._high_water = {}

    # -- entry point -------------------------------------------------------

    def evaluate(self, raw_contract, context=None, now=None):
        now = now or datetime.now(timezone.utc)
        result = contract_mod.intake(raw_contract, require_decision_fields=False)

        findings = []
        findings.extend(self._contract_findings(result))

        if result.contract is None:
            decision = decide(findings)
            return Evaluation(
                RUNTIME_NAME,
                decision,
                gate(decision),
                findings,
                "no inspectable contract; stopped at intake",
                result,
                None,
                self.policy.as_dict(),
            )

        c = result.contract
        findings.extend(self._authority_findings(c))
        findings.extend(self._admissibility_findings(c))
        findings.extend(self._temporal_findings(c, now))
        findings.extend(self._integrity_findings(c))
        findings.extend(self._replay_findings(c, context))
        binding_findings = self._binding_findings(c)
        findings.extend(binding_findings)
        findings.extend(self._evidence_findings(c))
        findings.extend(self._governance_findings(c))

        decision = decide(findings)

        # A verdict is only bound if the contract says BOUND and nothing in the
        # binding category disputes it. Otherwise the verdict is prose to us.
        bound_verdict = None
        if c.get("binding_status") == "BOUND" and not binding_findings:
            bound_verdict = c.get("re_verdict")
        decision_after = apply_bound_verdict(decision, bound_verdict)

        if decision_after is not decision:
            reason = "bound RE verdict %s honored as a denial" % bound_verdict
        elif findings:
            reason = "%d finding(s): %s" % (
                len(findings),
                ", ".join(sorted({f.primitive for f in findings})),
            )
        else:
            reason = "all typed checks passed and bound verdict is ALLOW"

        return Evaluation(
            RUNTIME_NAME,
            decision_after,
            gate(decision_after),
            findings,
            reason,
            result,
            bound_verdict,
            self.policy.as_dict(),
        )

    # -- categories --------------------------------------------------------

    def _contract_findings(self, result):
        out = []
        for d in result.defects:
            if d.code == contract_mod.D_MISSING:
                out.append(_f("CONTRACT_MISSING", None, d.detail))
            elif d.code == contract_mod.D_UNPARSABLE:
                out.append(_f("CONTRACT_UNPARSABLE", None, d.detail))
            elif d.code == contract_mod.D_UNSUPPORTED_VERSION:
                out.append(_f("CONTRACT_VERSION_DRIFT", d.field, d.detail))
            elif d.code == contract_mod.D_MISSING_METADATA:
                out.append(_f("CONTRACT_SCHEMA_MISMATCH", d.field, d.detail))
            elif d.code in (contract_mod.D_BAD_TYPE, contract_mod.D_BAD_ENUM):
                out.append(_f("CONTRACT_SCHEMA_MISMATCH", d.field, "%s: %s" % (d.code, d.detail)))

        if result.contract is not None:
            absent = [
                name
                for name in contract_mod.DECISION_FIELDS
                if not result.contract.has(name)
            ]
            if absent:
                out.append(
                    _f(
                        "CONTRACT_SEMANTICALLY_INCOMPLETE",
                        ",".join(absent),
                        "envelope is well formed but %d decision-bearing field(s) carry no value"
                        % len(absent),
                    )
                )
        return out

    def _authority_findings(self, c):
        out = []
        state = c.get("authority_state")
        if state == "LOST":
            out.append(_f("AUTHORITY_LOST", "authority_state", "authority_state=LOST"))
        elif state == "REVOKED":
            out.append(_f("AUTHORITY_REVOKED", "authority_state", "authority_state=REVOKED"))
        elif state == "MISMATCH":
            out.append(_f("AUTHORITY_MISMATCH", "authority_state", "authority_state=MISMATCH"))

        required = c.get("required_role")
        actor = c.get("actor_role")
        if required is not None and actor is not None and required != actor:
            out.append(
                _f(
                    "AUTHORITY_MISMATCH",
                    "actor_role",
                    "actor_role=%s does not satisfy required_role=%s" % (actor, required),
                )
            )
        return out

    def _admissibility_findings(self, c):
        state = c.get("admissibility_state")
        if state == "INADMISSIBLE":
            return [_f("INADMISSIBLE", "admissibility_state", "admissible = false")]
        if state == "UNKNOWN":
            return [
                _f(
                    "UNKNOWN",
                    "admissibility_state",
                    "admissibility_state=UNKNOWN; never converted to ALLOW",
                )
            ]
        return []

    def _temporal_findings(self, c, now):
        out = []
        issued = contract_mod.timestamp(c, "issued_at")
        expires = contract_mod.timestamp(c, "expires_at")
        not_before = contract_mod.timestamp(c, "not_before")

        if expires is not None and expires <= now:
            out.append(
                _f("EXPIRED", "expires_at", "expires_at=%s <= now=%s" % (expires.isoformat(), now.isoformat()))
            )
        if not_before is not None and not_before > now:
            out.append(
                _f(
                    "NOT_YET_VALID",
                    "not_before",
                    "not_before=%s > now=%s" % (not_before.isoformat(), now.isoformat()),
                )
            )
        if issued is not None and expires is not None and issued > expires:
            out.append(
                _f(
                    "TIMESTAMP_MISMATCH",
                    "issued_at",
                    "issued_at=%s is later than expires_at=%s" % (issued.isoformat(), expires.isoformat()),
                )
            )

        subject = c.get("subject") or c.get("authority_id")
        if issued is not None and subject is not None:
            previous = self._high_water.get(subject)
            if previous is not None and issued < previous:
                out.append(
                    _f(
                        "NON_MONOTONIC_TIME",
                        "issued_at",
                        "issued_at=%s precedes high-water mark %s for subject %s"
                        % (issued.isoformat(), previous.isoformat(), subject),
                    )
                )
            if previous is None or issued > previous:
                self._high_water[subject] = issued
        return out

    def _integrity_findings(self, c):
        out = []
        status = c.get("integrity_status")
        if status == "FAILED":
            out.append(_f("SIGNATURE_INVALID", "integrity_status", "integrity_status=FAILED"))
        elif status == "SIGNATURE_MISSING":
            out.append(_f("SIGNATURE_MISSING", "integrity_status", "integrity_status=SIGNATURE_MISSING"))
        elif status == "DIGEST_MISMATCH":
            out.append(_f("DIGEST_MISMATCH", "integrity_status", "integrity_status=DIGEST_MISMATCH"))

        signature = c.get("signature")
        if self.policy.signature_required and signature is None:
            out.append(
                _f(
                    "SIGNATURE_MISSING",
                    "signature",
                    "no signature field present; a claim of being signed is not a signature",
                )
            )
        elif signature is not None:
            expected = sign(c.typed)
            if not hmac.compare_digest(str(signature), expected):
                out.append(_f("SIGNATURE_INVALID", "signature", "recomputed signature does not match"))

        digest = c.get("payload_digest")
        if digest is not None:
            expected = hashlib.sha256(canonical_payload(c.typed)).hexdigest()
            if not hmac.compare_digest(str(digest), expected):
                out.append(_f("DIGEST_MISMATCH", "payload_digest", "recomputed digest does not match"))
        return out

    def _replay_findings(self, c, context):
        out = []
        nonce = c.get("nonce")
        request_id = c.get("request_id")

        if self.policy.nonce_required and nonce is None:
            out.append(
                _f("NONCE_REUSED", "nonce", "no nonce present; replay cannot be excluded")
            )
        elif nonce is not None:
            if nonce in self._nonces:
                out.append(_f("NONCE_REUSED", "nonce", "nonce %s already seen" % nonce))
            else:
                self._nonces.add(nonce)

        if request_id is not None:
            if request_id in self._requests:
                out.append(
                    _f("REQUEST_REPLAY", "request_id", "request_id %s already evaluated" % request_id)
                )
            else:
                self._requests.add(request_id)

        if context is not None:
            expected = context.get("request_id")
            if expected is not None and expected != request_id:
                out.append(
                    _f(
                        "CONTEXT_MISMATCH",
                        "request_id",
                        "contract request_id=%s but execution context expects %s"
                        % (request_id, expected),
                    )
                )
        return out

    def _binding_findings(self, c):
        out = []
        status = c.get("binding_status")
        if status == "MISSING":
            out.append(_f("BINDING_MISSING", "binding_status", "binding_status=MISSING"))
        elif status == "INVALID":
            out.append(_f("BINDING_INVALID", "binding_status", "binding_status=INVALID"))
        elif status == "UNMAPPED":
            out.append(
                _f(
                    "BINDING_UNMAPPED",
                    "binding_status",
                    "binding_status=UNMAPPED; unmapped is UNKNOWN, never a pass",
                )
            )
        elif status is None:
            out.append(_f("BINDING_MISSING", "binding_status", "binding_status absent"))

        declared = c.get("declared_primitives") or []
        if isinstance(declared, (list, tuple)):
            for name in declared:
                if not is_known(str(name), tier=TIER):
                    out.append(
                        _f(
                            "BINDING_UNMAPPED",
                            "declared_primitives",
                            "primitive %r is not in the runtime vocabulary; resolved to UNKNOWN, not to a pass"
                            % (name,),
                        )
                    )
        return out

    def _evidence_findings(self, c):
        if not self.policy.witness_required:
            return []
        out = []
        present = c.get("witness_present")
        status = c.get("witness_status")
        if present is not True:
            out.append(_f("WITNESS_MISSING", "witness_present", "witness_present=%r" % (present,)))
        elif status == "INVALID":
            out.append(_f("WITNESS_INVALID", "witness_status", "witness_status=INVALID"))
        elif status == "CONFLICT":
            out.append(_f("WITNESS_CONFLICT", "witness_status", "witness_status=CONFLICT"))
        elif status == "ABSENT":
            out.append(_f("WITNESS_MISSING", "witness_status", "witness_status=ABSENT"))
        return out

    def _governance_findings(self, c):
        out = []
        verdict = c.get("re_verdict")
        verdicts = c.get("re_verdicts")

        if isinstance(verdicts, (list, tuple)) and verdicts:
            values = set()
            for item in verdicts:
                if isinstance(item, dict):
                    values.add(item.get("verdict"))
                else:
                    values.add(item)
            if len(values) > 1:
                out.append(
                    _f(
                        "MULTIPLE_RE_CONFLICT",
                        "re_verdicts",
                        "conflicting verdicts: %s" % ", ".join(sorted(str(v) for v in values)),
                    )
                )
        elif verdict is None:
            out.append(_f("VERDICT_MISSING", "re_verdict", "no verdict field present"))

        claimed = c.get("verdict_digest")
        if claimed is not None and verdict is not None:
            if not hmac.compare_digest(str(claimed), verdict_digest(verdict)):
                out.append(
                    _f(
                        "VERDICT_MUTATED",
                        "verdict_digest",
                        "verdict_digest does not match re_verdict=%s" % verdict,
                    )
                )
        return out
