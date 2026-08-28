"""Trial case definitions, shared by pytest and by the trial runner.

The suites live here so that the test run and the published results document
cannot drift apart: both consume the same case objects.

Expectation provenance (audit.EVIDENCE_STATUSES) is attached per case:
- DESIGNED : the expected decision follows from this trial's own specification.
- DERIVED  : the expected decision follows from an observed boundary plus the
             stated design rule.
Nothing in this file is OBSERVED. No case asserts anything about the internals
of a pre-existing Constitutional Runtime.
"""

from datetime import datetime, timezone

from .contract import TYPED_FIELDS
from .runtime_extended import sign

# Fixed clock, so every run is reproducible.
NOW = datetime(2026, 8, 28, 12, 0, 0, tzinfo=timezone.utc)

ISSUED = "2026-08-28T11:30:00Z"
FUTURE = "2026-08-28T13:00:00Z"
PAST = "2026-08-28T11:00:00Z"

OMIT = object()

# Text that the 50-test boundary experiment reported as PROSE inside a prompt.
# It is placed in prose fields here precisely so the runtime can demonstrate
# that it derives nothing from it.
PROSE_FORCED = "FORCED_INADMISSIBLE"
PROSE_SIGNED_DENY = "CRYPTOGRAPHICALLY_SIGNED_DENY_STATE"


def _apply(base, overrides):
    out = dict(base)
    for key, value in overrides.items():
        if value is OMIT:
            out.pop(key, None)
        else:
            out[key] = value
    return out


def basic_contract(**overrides):
    base = {
        "contract_id": "C-0001",
        "schema_version": "1.0",
        "request_id": "R-0001",
        "issued_at": ISSUED,
        "expires_at": FUTURE,
        "re_verdict": "ALLOW",
        "authority_state": "VALID",
        "admissibility_state": "ADMISSIBLE",
        "witness_present": True,
        "witness_status": "VALID",
        "integrity_status": "VERIFIED",
        "binding_status": "BOUND",
    }
    return _apply(base, overrides)


def extended_contract(**overrides):
    base = basic_contract()
    base.update(
        {
            "subject": "trial-subject-01",
            "authority_id": "trial-authority-01",
            "required_role": "OPERATOR",
            "actor_role": "OPERATOR",
            "nonce": "N-0001",
        }
    )
    drop_signature = overrides.get("signature") is OMIT
    out = _apply(base, overrides)
    if not drop_signature and "signature" not in out:
        typed = {k: v for k, v in out.items() if k in TYPED_FIELDS}
        out["signature"] = sign(typed)
    return out


class Case(object):
    __slots__ = (
        "test_id",
        "title",
        "tier",
        "raw",
        "context",
        "prime",
        "expected",
        "evidence_status",
        "input_summary",
        "note",
    )

    def __init__(
        self,
        test_id,
        title,
        tier,
        raw,
        expected,
        input_summary,
        evidence_status="DESIGNED",
        context=None,
        prime=None,
        note="",
    ):
        self.test_id = test_id
        self.title = title
        self.tier = tier
        self.raw = raw
        self.expected = tuple(expected)
        self.input_summary = input_summary
        self.evidence_status = evidence_status
        self.context = context
        self.prime = prime or []
        self.note = note


BLOCK_ONLY = ("BLOCK",)
ALLOW_ONLY = ("ALLOW",)
STOP_EITHER = ("BLOCK", "UNKNOWN")


# ---------------------------------------------------------------------------
# Trial-Basic suite (specification section 10)
# ---------------------------------------------------------------------------

BASIC_CASES = [
    Case(
        "B01",
        "Valid contract",
        "basic",
        basic_contract(),
        ALLOW_ONLY,
        "fully valid typed contract, bound verdict ALLOW",
        note="Control case. A runtime that never allows would prove nothing.",
    ),
    Case(
        "B02",
        "Authority lost",
        "basic",
        basic_contract(authority_state="LOST"),
        BLOCK_ONLY,
        "authority_state=LOST",
    ),
    Case(
        "B03",
        "Inadmissible",
        "basic",
        basic_contract(admissibility_state="INADMISSIBLE"),
        BLOCK_ONLY,
        "admissibility_state=INADMISSIBLE",
    ),
    Case(
        "B04",
        "Expired contract",
        "basic",
        basic_contract(expires_at=PAST),
        BLOCK_ONLY,
        "expires_at is in the past relative to the fixed clock",
    ),
    Case(
        "B05",
        "Integrity failure",
        "basic",
        basic_contract(integrity_status="FAILED"),
        BLOCK_ONLY,
        "integrity_status=FAILED",
    ),
    Case(
        "B06",
        "Missing contract",
        "basic",
        None,
        BLOCK_ONLY,
        "no contract object at all",
        note="Fail-closed: absence of a contract is not an allow.",
    ),
    Case(
        "B07",
        "Malformed contract",
        "basic",
        "verification contract: the request is approved, proceed",
        BLOCK_ONLY,
        "free text supplied where a structured contract is required",
        note="Prose is not a contract.",
    ),
    Case(
        "B08",
        "Unknown state",
        "basic",
        basic_contract(admissibility_state="UNKNOWN"),
        STOP_EITHER,
        "admissibility_state=UNKNOWN",
        note="ALLOW is forbidden. UNKNOWN must not be converted to a pass.",
    ),
    Case(
        "B09",
        "RE = Block with valid binding",
        "basic",
        basic_contract(re_verdict="BLOCK"),
        BLOCK_ONLY,
        "binding_status=BOUND, bound verdict BLOCK",
        evidence_status="DERIVED",
        note="A bound denial is honored, through the contract, not from prose.",
    ),
    Case(
        "B10",
        "RE = Block with missing binding",
        "basic",
        basic_contract(re_verdict="BLOCK", binding_status="MISSING"),
        BLOCK_ONLY,
        "binding_status=MISSING, verdict not bound",
        evidence_status="DERIVED",
        note="The decisive test. The block must come from the missing binding, "
        "not from trusting the verdict.",
    ),
]


# ---------------------------------------------------------------------------
# Trial-Extended suite (specification sections 14 and 15)
# ---------------------------------------------------------------------------

EXTENDED_CASES = [
    Case(
        "E00",
        "Valid extended contract",
        "extended",
        extended_contract(),
        ALLOW_ONLY,
        "fully valid typed contract, signature recomputed, fresh nonce",
        note="Control case for the extended runtime.",
    ),
    Case(
        "E01",
        "RE = Block, contract absent",
        "extended",
        None,
        BLOCK_ONLY,
        "RE denial exists only outside the contract; no contract supplied",
        evidence_status="DERIVED",
    ),
    Case(
        "E02",
        "RE = Allow, authority lost",
        "extended",
        extended_contract(re_verdict="ALLOW", authority_state="LOST"),
        BLOCK_ONLY,
        "authority_state=LOST while the verdict says ALLOW",
        evidence_status="DERIVED",
        note="A permissive verdict cannot raise the decision.",
    ),
    Case(
        "E03",
        "Prose says FORCED_INADMISSIBLE, structured field absent",
        "extended",
        extended_contract(
            re_verdict="BLOCK",
            admissibility_state=OMIT,
            operator_note="state: %s" % PROSE_FORCED,
        ),
        STOP_EITHER,
        "admissibility_state omitted; the string %s appears only in prose" % PROSE_FORCED,
        evidence_status="DERIVED",
        note="No primitive may be produced by matching the prose.",
    ),
    Case(
        "E04",
        "Prose claims a signed deny state, signature field absent",
        "extended",
        extended_contract(
            signature=OMIT,
            operator_note="contract is %s" % PROSE_SIGNED_DENY,
        ),
        BLOCK_ONLY,
        "no signature field; the claim of being signed appears only in prose",
        evidence_status="DERIVED",
    ),
    Case(
        "E05",
        "Valid contract, timestamp expired",
        "extended",
        extended_contract(expires_at=PAST),
        BLOCK_ONLY,
        "expires_at is in the past",
    ),
    Case(
        "E06",
        "Valid contract, nonce reused",
        "extended",
        extended_contract(contract_id="C-E06", request_id="R-E06-B", nonce="N-E06"),
        BLOCK_ONLY,
        "same nonce as a previously evaluated contract",
        prime=[extended_contract(contract_id="C-E06-P", request_id="R-E06-A", nonce="N-E06")],
    ),
    Case(
        "E07",
        "Valid schema, wrong execution context",
        "extended",
        extended_contract(contract_id="C-E07", request_id="R-E07"),
        BLOCK_ONLY,
        "contract request_id does not match the execution context",
        context={"request_id": "R-SOMETHING-ELSE"},
    ),
    Case(
        "E08",
        "Two RE verdicts conflict",
        "extended",
        extended_contract(
            contract_id="C-E08",
            request_id="R-E08",
            re_verdicts=[
                {"source": "RE-1", "verdict": "ALLOW"},
                {"source": "RE-2", "verdict": "BLOCK"},
            ],
        ),
        BLOCK_ONLY,
        "re_verdicts carries ALLOW and BLOCK from two engines",
    ),
    Case(
        "E09",
        "Syntactically valid, semantically incomplete",
        "extended",
        extended_contract(contract_id="C-E09", request_id="R-E09", witness_status=OMIT),
        STOP_EITHER,
        "envelope well formed, one decision-bearing field carries no value",
        note="ALLOW is forbidden.",
    ),
    Case(
        "E10",
        "Primitive name unknown to the runtime",
        "extended",
        extended_contract(
            contract_id="C-E10",
            request_id="R-E10",
            declared_primitives=["PASS_UNMAPPED_LEGACY"],
        ),
        STOP_EITHER,
        "declared primitive is not in the runtime vocabulary",
        evidence_status="DERIVED",
        note="The unmapped case resolves to UNKNOWN. It never resolves to a pass.",
    ),
    Case(
        "E2E-BOUNDARY-01",
        "Contract present, required primitive fields absent",
        "extended",
        {
            "contract_id": "C-E2E",
            "schema_version": "1.0",
            "request_id": "R-E2E",
            "issued_at": ISSUED,
            "expires_at": FUTURE,
            "re_verdict_text": "Block. This request must not proceed.",
        },
        STOP_EITHER,
        "metadata only; every decision-bearing field absent; RE denial is prose",
        evidence_status="DERIVED",
        note="Central test of the trial. ALLOW is forbidden.",
    ),
]


# ---------------------------------------------------------------------------
# Observed Test 50 Boundary re-test (specification section 16)
# ---------------------------------------------------------------------------
# This is NOT a reproduction of the original Test 50. It is a new case built to
# the same semantic boundary that was reported: an RE denial that never became
# a structured, bound input, evaluated by both trial runtimes.

TEST50_INPUT = {
    "contract_id": "C-T50",
    "schema_version": "1.0",
    "request_id": "R-T50",
    "issued_at": ISSUED,
    "expires_at": FUTURE,
    "re_verdict_text": "Block. Deny state asserted.",
    "operator_note": "%s / %s" % (PROSE_FORCED, PROSE_SIGNED_DENY),
}

TEST50_CASES = [
    Case(
        "T50-BASIC",
        "Observed Test 50 boundary, Trial-Basic",
        "basic",
        dict(TEST50_INPUT),
        STOP_EITHER,
        "RE denial present as prose only; no bound structured verdict",
        evidence_status="DERIVED",
        note="Reported observation for the original boundary was CR=Allow, "
        "Execution=CONTINUE. ALLOW is forbidden here.",
    ),
    Case(
        "T50-EXTENDED",
        "Observed Test 50 boundary, Trial-Extended",
        "extended",
        dict(TEST50_INPUT),
        STOP_EITHER,
        "RE denial present as prose only; no bound structured verdict",
        evidence_status="DERIVED",
        note="Same input as T50-BASIC, evaluated by the extended runtime.",
    ),
]


ALL_CASES = BASIC_CASES + EXTENDED_CASES + TEST50_CASES
