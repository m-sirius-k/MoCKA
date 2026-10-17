"""Active Authority Registry (HG-RCL-20261004-004, area A).

Role: REGISTRY (DERIVED from Human Gate Decision Records). This module does NOT
generate authority. It only reflects Human Gate Decision Records that already
exist on disk. It is fully separated from data/decisions/decision_ledger.jsonl
(the Phase-1 frozen ledger); there is NO fallback to that ledger.

Runtime Gate rule: a run is authorized iff its Human Gate authority id is
  registered  AND  status valid  AND  not expired  AND  not revoked  AND
  scope matches  AND  the source is a Human Gate Decision Record (not a
  self-citing evidence/implementation artifact).

UNKNOWN / missing / expired / revoked / scope-mismatch are never ALLOW.
AI / JARVIS / HAB / Memory cannot self-update the registry.
ASCII-only per TODO_333.
"""
from __future__ import annotations

import os
import json
from datetime import datetime, timezone

# Subjects that may never write to or expand the registry (self-update ban).
BANNED_WRITERS = {"AI", "JARVIS", "HAB", "Memory", "Reassessment", "Runtime",
                  "Assessment", "Experience Memory"}

_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DEFAULT_REGISTRY = os.path.join(_REPO, "governance", "authority_registry",
                                 "authority_registry.json")

# Result states (none of these except REGISTERED_VALID is ALLOW).
REGISTERED_VALID = "REGISTERED_VALID"
UNREGISTERED = "UNREGISTERED"
INVALID_AUTHORITY = "INVALID_AUTHORITY"
INVALID_STATUS = "INVALID_STATUS"
EXPIRED = "EXPIRED"
REVOKED = "REVOKED"
SCOPE_MISMATCH = "SCOPE_MISMATCH"
SELF_UPDATE_DENIED = "SELF_UPDATE_DENIED"


def _parse_iso(s: str):
    try:
        return datetime.fromisoformat((s or "").replace("Z", "+00:00"))
    except Exception:
        return None


class AuthorityRegistry:
    """Read-only-at-runtime registry of Human Gate authorities."""

    def __init__(self, registry_path: str = _DEFAULT_REGISTRY, repo_root: str = _REPO):
        self._path = registry_path
        self._repo = repo_root
        self._entries = {}
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self._path):
            self._entries = {}
            return
        with open(self._path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for e in data.get("entries", []):
            did = e.get("decision_id")
            if did:
                self._entries[did] = e

    def is_present(self, decision_id: str) -> bool:
        return decision_id in self._entries

    def get(self, decision_id: str) -> dict:
        return dict(self._entries.get(decision_id, {}))

    def check(self, decision_id: str, requested_scope: str, now=None,
              caller_source: str = "runtime") -> dict:
        """Return a decision dict: {ok, state, reasons, decision_id}.

        ok is True only for REGISTERED_VALID. Everything else is DENY.
        caller_source is informational for the read path; writes are guarded
        separately by register()/revoke().
        """
        now = now or datetime.now(timezone.utc)
        reasons = []

        entry = self._entries.get(decision_id)
        if entry is None:
            return {"ok": False, "state": UNREGISTERED,
                    "reasons": ["decision_id not registered"], "decision_id": decision_id}

        # Authority must be Human Gate, and the source must be an AUTHORITY
        # artifact (a Human Gate Decision Record), never a self-citing
        # evidence/implementation artifact (NT-G).
        if entry.get("authority") != "Human Gate":
            reasons.append("authority is not Human Gate")
            return {"ok": False, "state": INVALID_AUTHORITY, "reasons": reasons,
                    "decision_id": decision_id}
        if entry.get("source_role") != "AUTHORITY":
            reasons.append("source_record is not a Human Gate Decision Record "
                           "(self-citation / evidence-as-authority rejected)")
            return {"ok": False, "state": INVALID_AUTHORITY, "reasons": reasons,
                    "decision_id": decision_id}
        src = entry.get("source_record", "")
        if not src or not os.path.exists(os.path.join(self._repo, src)):
            reasons.append("source Human Gate Decision Record file is missing")
            return {"ok": False, "state": INVALID_AUTHORITY, "reasons": reasons,
                    "decision_id": decision_id}

        # Registration state / status
        if entry.get("registration_state") == "REVOKED" or entry.get("status") == "REVOKED":
            return {"ok": False, "state": REVOKED, "reasons": ["decision revoked"],
                    "decision_id": decision_id}
        if entry.get("status") != "APPROVED":
            return {"ok": False, "state": INVALID_STATUS,
                    "reasons": ["status=%s" % entry.get("status")], "decision_id": decision_id}

        # Temporal validity
        eff = _parse_iso(entry.get("effective_from"))
        unt = _parse_iso(entry.get("effective_until"))
        if unt is not None and now >= unt:
            return {"ok": False, "state": EXPIRED, "reasons": ["past effective_until"],
                    "decision_id": decision_id}
        if eff is not None and now < eff:
            return {"ok": False, "state": INVALID_STATUS, "reasons": ["before effective_from"],
                    "decision_id": decision_id}

        # Scope coverage
        allowed = entry.get("authorized_scope", []) or []
        prohibited = entry.get("prohibited_scope", []) or []
        if requested_scope in prohibited:
            return {"ok": False, "state": SCOPE_MISMATCH,
                    "reasons": ["requested scope is prohibited"], "decision_id": decision_id}
        if "*" not in allowed and requested_scope not in allowed:
            return {"ok": False, "state": SCOPE_MISMATCH,
                    "reasons": ["requested scope not in authorized_scope"],
                    "decision_id": decision_id}

        return {"ok": True, "state": REGISTERED_VALID,
                "reasons": ["registered, valid, in scope"], "decision_id": decision_id}

    # --- write guards (not used by the runtime read path) ---
    def register(self, entry: dict, caller_source: str = "Human Gate") -> dict:
        """Guarded registration. Rejects banned writers and self-generation.

        A registration is only accepted when the caller is the Human Gate and a
        real Human Gate Decision Record file (source_role=AUTHORITY) exists. The
        registry never invents authority.
        """
        if caller_source in BANNED_WRITERS or caller_source != "Human Gate":
            return {"ok": False, "state": SELF_UPDATE_DENIED,
                    "reasons": ["caller may not write the registry: %s" % caller_source]}
        if entry.get("authority") != "Human Gate" or entry.get("source_role") != "AUTHORITY":
            return {"ok": False, "state": INVALID_AUTHORITY,
                    "reasons": ["registration requires a Human Gate Decision Record"]}
        src = entry.get("source_record", "")
        if not src or not os.path.exists(os.path.join(self._repo, src)):
            return {"ok": False, "state": INVALID_AUTHORITY,
                    "reasons": ["source Decision Record file missing"]}
        self._entries[entry["decision_id"]] = dict(entry)
        return {"ok": True, "state": "REGISTERED", "reasons": ["registered"]}
