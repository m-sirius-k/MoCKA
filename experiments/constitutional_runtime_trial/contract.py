"""Typed Verification Contract intake for the MoCKA CR Trial.

Central architectural rule enforced here:

    Prose is not a Primitive.

Any key that is not part of the declared typed schema is moved into a prose
quarantine. The quarantine is carried for audit only. No evaluator in this
package reads it, and no primitive is ever derived by scanning text.

Intake never raises a decision. It returns tier-neutral DEFECT CODES, and each
runtime maps those codes to primitives from its own tier vocabulary. That keeps
Trial-Basic's small primitive set and Trial-Extended's split vocabulary honest
about being two different designs over one intake.
"""

from datetime import datetime

# --- schema ---------------------------------------------------------------

SCHEMA_VERSION_CURRENT = "1.0"
SCHEMA_VERSIONS_SUPPORTED = ("1.0",)

# Metadata: identifies the contract. Absence means the contract is not a
# contract at all.
METADATA_FIELDS = (
    "contract_id",
    "schema_version",
    "request_id",
    "issued_at",
    "expires_at",
)

# Decision-bearing: the typed fields the runtime is allowed to reason over.
# Absence means the contract identifies itself but carries no decidable state.
DECISION_FIELDS = (
    "re_verdict",
    "authority_state",
    "admissibility_state",
    "witness_present",
    "witness_status",
    "integrity_status",
    "binding_status",
)

# Extended-only typed fields. Optional at intake; the extended runtime decides
# what their absence means.
EXTENDED_FIELDS = (
    "not_before",
    "subject",
    "authority_id",
    "required_role",
    "actor_role",
    "nonce",
    "signature",
    "payload_digest",
    "re_verdicts",
    "verdict_digest",
    "declared_primitives",
)

TYPED_FIELDS = METADATA_FIELDS + DECISION_FIELDS + EXTENDED_FIELDS

ENUMS = {
    "re_verdict": ("ALLOW", "BLOCK", "UNKNOWN"),
    "authority_state": ("VALID", "LOST", "REVOKED", "MISMATCH"),
    "admissibility_state": ("ADMISSIBLE", "INADMISSIBLE", "UNKNOWN"),
    "witness_status": ("VALID", "INVALID", "ABSENT", "CONFLICT"),
    "integrity_status": ("VERIFIED", "FAILED", "SIGNATURE_MISSING", "DIGEST_MISMATCH"),
    "binding_status": ("BOUND", "MISSING", "INVALID", "UNMAPPED"),
}

TIMESTAMP_FIELDS = ("issued_at", "expires_at", "not_before")


# --- defect codes (tier neutral) ------------------------------------------

D_MISSING = "MISSING"
D_UNPARSABLE = "UNPARSABLE"
D_UNSUPPORTED_VERSION = "UNSUPPORTED_SCHEMA_VERSION"
D_MISSING_METADATA = "MISSING_METADATA_FIELD"
D_MISSING_DECISION = "MISSING_DECISION_FIELD"
D_BAD_TYPE = "BAD_TYPE"
D_BAD_ENUM = "BAD_ENUM"


class Defect(object):
    __slots__ = ("code", "field", "detail")

    def __init__(self, code, field=None, detail=""):
        self.code = code
        self.field = field
        self.detail = detail

    def as_dict(self):
        return {"code": self.code, "field": self.field, "detail": self.detail}

    def __repr__(self):
        return "Defect(%s, %r)" % (self.code, self.field)


class VerificationContract(object):
    """A contract that survived intake far enough to be inspected.

    `typed` holds only schema fields. `prose` holds everything else and is
    never consulted by an evaluator.
    """

    __slots__ = ("typed", "prose", "raw_kind")

    def __init__(self, typed, prose, raw_kind):
        self.typed = typed
        self.prose = prose
        self.raw_kind = raw_kind

    def get(self, field, default=None):
        """Typed access only. A field outside the schema is never reachable."""
        if field not in TYPED_FIELDS:
            raise KeyError(
                "field %r is not a typed schema field; prose is not a primitive" % (field,)
            )
        return self.typed.get(field, default)

    def has(self, field):
        return field in self.typed and self.typed[field] is not None

    def prose_keys(self):
        """Audit-only view. Returns key names, never values."""
        return tuple(sorted(self.prose.keys()))

    def as_dict(self):
        return {
            "raw_kind": self.raw_kind,
            "typed": dict(self.typed),
            "prose_keys": list(self.prose_keys()),
        }


class IntakeResult(object):
    __slots__ = ("contract", "defects")

    def __init__(self, contract, defects):
        self.contract = contract
        self.defects = defects

    @property
    def ok(self):
        return not self.defects

    def codes(self):
        return tuple(d.code for d in self.defects)

    def as_dict(self):
        return {
            "contract": self.contract.as_dict() if self.contract else None,
            "defects": [d.as_dict() for d in self.defects],
        }


def _parse_timestamp(value):
    if not isinstance(value, str):
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def intake(raw, require_decision_fields=True):
    """Turn an arbitrary inbound object into a typed contract plus defects.

    raw may be:
      None            -> D_MISSING
      str / bytes     -> D_UNPARSABLE (free text is not a contract)
      anything else   -> D_UNPARSABLE
      dict            -> typed validation
    """
    if raw is None:
        return IntakeResult(None, [Defect(D_MISSING, None, "no contract supplied")])

    if isinstance(raw, (str, bytes, bytearray)):
        return IntakeResult(
            None,
            [Defect(D_UNPARSABLE, None, "inbound object is free text, not a structured contract")],
        )

    if not isinstance(raw, dict):
        return IntakeResult(
            None,
            [Defect(D_UNPARSABLE, None, "inbound object type %s is not a structured contract" % type(raw).__name__)],
        )

    typed = {}
    prose = {}
    for key, value in raw.items():
        if key in TYPED_FIELDS:
            typed[key] = value
        else:
            prose[key] = value

    contract = VerificationContract(typed, prose, raw_kind="mapping")
    defects = []

    for field in METADATA_FIELDS:
        if typed.get(field) is None:
            defects.append(Defect(D_MISSING_METADATA, field, "required metadata field absent"))

    version = typed.get("schema_version")
    if version is not None and version not in SCHEMA_VERSIONS_SUPPORTED:
        defects.append(
            Defect(D_UNSUPPORTED_VERSION, "schema_version", "version %r is not supported" % (version,))
        )

    if require_decision_fields:
        for field in DECISION_FIELDS:
            if field not in typed or typed[field] is None:
                defects.append(
                    Defect(D_MISSING_DECISION, field, "decision-bearing field absent or null")
                )

    for field in TIMESTAMP_FIELDS:
        value = typed.get(field)
        if value is not None and _parse_timestamp(value) is None:
            defects.append(Defect(D_BAD_TYPE, field, "not an ISO-8601 timestamp"))

    if typed.get("witness_present") is not None and not isinstance(typed["witness_present"], bool):
        defects.append(Defect(D_BAD_TYPE, "witness_present", "not a boolean"))

    for field, allowed in ENUMS.items():
        value = typed.get(field)
        if value is not None and value not in allowed:
            defects.append(
                Defect(D_BAD_ENUM, field, "value %r not in %s" % (value, ",".join(allowed)))
            )

    if typed.get("re_verdicts") is not None and not isinstance(typed["re_verdicts"], (list, tuple)):
        defects.append(Defect(D_BAD_TYPE, "re_verdicts", "not a list"))

    if typed.get("declared_primitives") is not None and not isinstance(
        typed["declared_primitives"], (list, tuple)
    ):
        defects.append(Defect(D_BAD_TYPE, "declared_primitives", "not a list"))

    return IntakeResult(contract, defects)


def timestamp(contract, field):
    """Parsed timestamp for a typed field, or None."""
    return _parse_timestamp(contract.get(field))
