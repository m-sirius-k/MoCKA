"""Primitive vocabulary for the MoCKA Constitutional Runtime Trial.

EVIDENCE BOUNDARY
-----------------
Every name in this module is DESIGNED for this trial.

Some names resemble labels reported from the 50-test boundary experiment
(AUTHORITY_LOST, INADMISSIBLE, ...). Those reported strings are treated as
"Observed / normalized label" only. It is NOT claimed that any pre-existing
Constitutional Runtime used these as internal primitive names. That remains
NOT OBSERVED.

Deliberately NOT adopted as a primitive name:
- "ADMISSIBLE (Fail)"  -> the trial uses INADMISSIBLE / admissible = false.
- "PASS (Unmapped)"    -> the trial uses BINDING_UNMAPPED, which resolves to
                          UNKNOWN, never to a pass.
"""

from enum import Enum


class Decision(str, Enum):
    """Internal decision state of the Constitutional Runtime."""

    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


class Execution(str, Enum):
    """Execution gateway outcome."""

    EXECUTE = "EXECUTE"
    STOP = "STOP"


class Severity(str, Enum):
    """How a raised primitive contributes to the decision.

    BLOCKING      -> forces BLOCK.
    INDETERMINATE -> forces at least UNKNOWN. Never ALLOW.
    """

    BLOCKING = "BLOCKING"
    INDETERMINATE = "INDETERMINATE"


class Category(str, Enum):
    CONTRACT = "Contract"
    AUTHORITY = "Authority"
    ADMISSIBILITY = "Admissibility"
    TEMPORAL = "Temporal"
    INTEGRITY = "Integrity"
    REPLAY = "Replay"
    BINDING = "Binding"
    EVIDENCE = "Evidence"
    GOVERNANCE = "Governance"


# ---------------------------------------------------------------------------
# Primitive registry
# ---------------------------------------------------------------------------
# tier: "basic"    -> defined in Trial-Basic (and inherited by Trial-Extended)
#       "extended" -> defined in Trial-Extended only
#
# origin: "instruction-listed" -> the name appears in the Dr. Kimura trial
#                                 specification (sections 6 and 12)
#         "trial-added"        -> added by this trial beyond that list; the
#                                 addition is disclosed in the design docs
# ---------------------------------------------------------------------------

_REGISTRY = {
    # -- Contract ----------------------------------------------------------
    "CONTRACT_INVALID": (Category.CONTRACT, Severity.BLOCKING, "basic", "instruction-listed"),
    "CONTRACT_MISSING": (Category.CONTRACT, Severity.BLOCKING, "extended", "instruction-listed"),
    "CONTRACT_UNPARSABLE": (Category.CONTRACT, Severity.BLOCKING, "extended", "instruction-listed"),
    "CONTRACT_SCHEMA_MISMATCH": (Category.CONTRACT, Severity.BLOCKING, "extended", "instruction-listed"),
    "CONTRACT_VERSION_DRIFT": (Category.CONTRACT, Severity.BLOCKING, "extended", "instruction-listed"),
    "CONTRACT_SEMANTICALLY_INCOMPLETE": (Category.CONTRACT, Severity.INDETERMINATE, "extended", "trial-added"),
    # -- Authority ---------------------------------------------------------
    "AUTHORITY_LOST": (Category.AUTHORITY, Severity.BLOCKING, "basic", "instruction-listed"),
    "AUTHORITY_REVOKED": (Category.AUTHORITY, Severity.BLOCKING, "extended", "instruction-listed"),
    "AUTHORITY_MISMATCH": (Category.AUTHORITY, Severity.BLOCKING, "extended", "instruction-listed"),
    # -- Admissibility -----------------------------------------------------
    "INADMISSIBLE": (Category.ADMISSIBILITY, Severity.BLOCKING, "basic", "instruction-listed"),
    "UNKNOWN": (Category.ADMISSIBILITY, Severity.INDETERMINATE, "basic", "instruction-listed"),
    # -- Temporal ----------------------------------------------------------
    "EXPIRED": (Category.TEMPORAL, Severity.BLOCKING, "basic", "instruction-listed"),
    "NOT_YET_VALID": (Category.TEMPORAL, Severity.BLOCKING, "extended", "instruction-listed"),
    "TIMESTAMP_MISMATCH": (Category.TEMPORAL, Severity.BLOCKING, "extended", "instruction-listed"),
    "NON_MONOTONIC_TIME": (Category.TEMPORAL, Severity.BLOCKING, "extended", "instruction-listed"),
    # -- Integrity ---------------------------------------------------------
    "INTEGRITY_FAILURE": (Category.INTEGRITY, Severity.BLOCKING, "basic", "instruction-listed"),
    "SIGNATURE_INVALID": (Category.INTEGRITY, Severity.BLOCKING, "extended", "instruction-listed"),
    "SIGNATURE_MISSING": (Category.INTEGRITY, Severity.BLOCKING, "extended", "instruction-listed"),
    "DIGEST_MISMATCH": (Category.INTEGRITY, Severity.BLOCKING, "extended", "instruction-listed"),
    # -- Replay ------------------------------------------------------------
    "NONCE_REUSED": (Category.REPLAY, Severity.BLOCKING, "extended", "instruction-listed"),
    "REQUEST_REPLAY": (Category.REPLAY, Severity.BLOCKING, "extended", "instruction-listed"),
    "CONTEXT_MISMATCH": (Category.REPLAY, Severity.BLOCKING, "extended", "instruction-listed"),
    # -- Binding -----------------------------------------------------------
    "BINDING_MISSING": (Category.BINDING, Severity.BLOCKING, "extended", "instruction-listed"),
    "BINDING_INVALID": (Category.BINDING, Severity.BLOCKING, "extended", "instruction-listed"),
    "BINDING_UNMAPPED": (Category.BINDING, Severity.INDETERMINATE, "extended", "instruction-listed"),
    # -- Evidence ----------------------------------------------------------
    "WITNESS_MISSING": (Category.EVIDENCE, Severity.BLOCKING, "extended", "instruction-listed"),
    "WITNESS_INVALID": (Category.EVIDENCE, Severity.BLOCKING, "extended", "instruction-listed"),
    "WITNESS_CONFLICT": (Category.EVIDENCE, Severity.BLOCKING, "extended", "instruction-listed"),
    # -- Governance --------------------------------------------------------
    "MULTIPLE_RE_CONFLICT": (Category.GOVERNANCE, Severity.BLOCKING, "extended", "instruction-listed"),
    "VERDICT_MISSING": (Category.GOVERNANCE, Severity.BLOCKING, "extended", "instruction-listed"),
    "VERDICT_MUTATED": (Category.GOVERNANCE, Severity.BLOCKING, "extended", "instruction-listed"),
}

BASIC_PRIMITIVES = tuple(n for n, v in _REGISTRY.items() if v[2] == "basic")
EXTENDED_PRIMITIVES = tuple(_REGISTRY.keys())


class UnknownPrimitiveError(KeyError):
    """Raised when a primitive name is not in the registry.

    The runtime never resolves an unknown primitive name to a pass. Callers
    that receive this must map it to BINDING_UNMAPPED (INDETERMINATE).
    """


def severity_of(name, tier="extended"):
    """Return the Severity of a primitive name for the given tier."""
    entry = _REGISTRY.get(name)
    if entry is None:
        raise UnknownPrimitiveError(name)
    if tier == "basic" and entry[2] != "basic":
        raise UnknownPrimitiveError(name)
    return entry[1]


def category_of(name):
    entry = _REGISTRY.get(name)
    if entry is None:
        raise UnknownPrimitiveError(name)
    return entry[0]


def origin_of(name):
    entry = _REGISTRY.get(name)
    if entry is None:
        raise UnknownPrimitiveError(name)
    return entry[3]


def is_known(name, tier="extended"):
    try:
        severity_of(name, tier=tier)
        return True
    except UnknownPrimitiveError:
        return False


class Finding(object):
    """One raised primitive plus the typed field that raised it."""

    __slots__ = ("primitive", "severity", "category", "field", "detail")

    def __init__(self, primitive, severity, category, field, detail):
        self.primitive = primitive
        self.severity = severity
        self.category = category
        self.field = field
        self.detail = detail

    def as_dict(self):
        return {
            "primitive": self.primitive,
            "severity": self.severity.value,
            "category": self.category.value,
            "field": self.field,
            "detail": self.detail,
        }

    def __repr__(self):
        return "Finding(%s, field=%r)" % (self.primitive, self.field)


def decide(findings):
    """Reduce findings to a Decision.

    Rules:
    - any BLOCKING finding      -> BLOCK
    - else any INDETERMINATE    -> UNKNOWN
    - else                      -> ALLOW

    UNKNOWN is never silently converted to ALLOW. That is the whole point of
    keeping INDETERMINATE as a separate severity instead of a boolean.
    """
    if any(f.severity is Severity.BLOCKING for f in findings):
        return Decision.BLOCK
    if any(f.severity is Severity.INDETERMINATE for f in findings):
        return Decision.UNKNOWN
    return Decision.ALLOW
