"""
Tests for comprehensive Assessment admissibility and MemoryStore unification.

Encodes the design decisions from きむら博士 (2026-10-02):
  - confidence alone does NOT determine admissibility
  - UNKNOWN != FALSE
  - UNKNOWN != auto-ALLOW
  - Evidence absent -> DENY regardless of confidence
  - Freshness expired -> DENY regardless of confidence
  - Interpretation not separated -> DENY regardless of confidence
  - Memory write uses MemoryStore.append() exclusively (no direct JSON write)
  - Retention policy and memory_id applied via MemoryStore
"""
import os
import tempfile
import pytest
from pathlib import Path


def _all_axes(x="evidence present", y="interpretation of evidence", z="authority context",
              t="valid and fresh", s="low social impact", k="structural rules apply"):
    return {"X": x, "Y": y, "Z": z, "T": t, "S": s, "K": k}


class TestComprehensiveAdmissibility:
    """Tests for comprehensive admissibility (contract-based, not confidence-only)."""

    def test_A01_high_confidence_evidence_absent_denies(self):
        """A-01: confidence high + Evidence (X) absent -> inadmissible.
        Verifies: confidence >= threshold alone does NOT make admissible.
        """
        from aur.assessment import create_assessment
        axes = _all_axes(x=None)  # Evidence absent (None, not UNKNOWN)
        record = create_assessment("action-A01", axes=axes, assessor="test")
        assert record.admissible == False, (
            f"Evidence absent must be inadmissible. Got reason: {record.reason}"
        )
        assert "evidence" in record.reason.lower() or "X" in record.reason, (
            f"Reason must reference Evidence/X axis. Got: {record.reason}"
        )

    def test_A02_high_confidence_freshness_expired_denies(self):
        """A-02: confidence high + Freshness (T) expired -> inadmissible.
        Verifies: freshness failure denies regardless of evidence quality.
        """
        from aur.assessment import create_assessment
        axes = _all_axes(t="expired")
        record = create_assessment("action-A02", axes=axes, assessor="test")
        assert record.admissible == False, (
            f"Expired freshness must be inadmissible. Got reason: {record.reason}"
        )
        assert "fresh" in record.reason.lower() or "T" in record.reason or "expired" in record.reason.lower(), (
            f"Reason must reference Freshness/T/expired. Got: {record.reason}"
        )

    def test_A03_high_confidence_interpretation_not_separated_denies(self):
        """A-03: confidence high + Y identical to X -> inadmissible.
        Verifies: interpretation must be analytically separated from evidence.
        """
        from aur.assessment import create_assessment
        same_value = "file exists at path /foo/bar"
        axes = _all_axes(x=same_value, y=same_value)  # Y == X, not separated
        record = create_assessment("action-A03", axes=axes, assessor="test")
        assert record.admissible == False, (
            f"Non-separated interpretation must be inadmissible. Got reason: {record.reason}"
        )
        assert (
            "interpretation" in record.reason.lower()
            or "Y" in record.reason
            or "separated" in record.reason.lower()
        ), f"Reason must reference Interpretation/Y/separation. Got: {record.reason}"

    def test_A04_unknown_is_not_false(self):
        """A-04: UNKNOWN axis != FALSE.
        UNKNOWN on an axis reduces confidence but does not equal a negative assertion.
        When confidence is still >= threshold, assessment can be admissible.
        """
        from aur.assessment import create_assessment
        # Only one axis UNKNOWN; others concrete. Confidence: 1.0 - 0.15 = 0.85 >= 0.5
        axes = _all_axes(s="UNKNOWN")  # S=UNKNOWN, rest concrete
        record = create_assessment("action-A04", axes=axes, assessor="test")
        # UNKNOWN on S alone should not cause inadmissible
        assert record.admissible == True, (
            f"Single UNKNOWN axis should not deny when confidence >= threshold. "
            f"Got admissible={record.admissible}, confidence={record.confidence:.2f}, "
            f"reason={record.reason}"
        )
        assert record.confidence < 1.0, "UNKNOWN axis must reduce confidence below 1.0"

    def test_A05_unknown_is_not_auto_allow(self):
        """A-05: UNKNOWN != auto-ALLOW.
        All axes UNKNOWN -> confidence severely reduced -> inadmissible via confidence gate.
        The reason is confidence, not that UNKNOWN means False.
        """
        from aur.assessment import create_assessment
        axes = {k: "UNKNOWN" for k in ["X", "Y", "Z", "T", "S", "K"]}
        # Note: X = "UNKNOWN" (not None/empty) -> evidence unknown, not absent
        # BUT: confidence = 1.0 - 6*0.15 = 0.1 < 0.5 -> inadmissible via confidence gate
        record = create_assessment("action-A05", axes=axes, assessor="test")
        assert record.admissible == False, (
            f"All-UNKNOWN assessment must be inadmissible due to low confidence. "
            f"Got admissible={record.admissible}, confidence={record.confidence:.2f}"
        )
        assert record.confidence < 0.5, (
            f"All-UNKNOWN should yield confidence < 0.5. Got {record.confidence:.2f}"
        )
        # The denial must be due to confidence, not Evidence being absent
        # (X="UNKNOWN" is not the same as X=None which is "absent")
        assert "confidence" in record.reason.lower(), (
            f"Denial reason must cite confidence (not Evidence absent). Got: {record.reason}"
        )

    def test_A06_all_conditions_met_is_admissible(self):
        """A-06: all admissibility conditions satisfied -> admissible=True.
        Positive test: when all conditions hold, assessment is admitted.
        """
        from aur.assessment import create_assessment
        axes = _all_axes()  # All concrete, separated, fresh
        record = create_assessment("action-A06", axes=axes, assessor="test")
        assert record.admissible == True, (
            f"All conditions met must be admissible. Got reason: {record.reason}"
        )
        assert record.confidence >= 0.5, (
            f"Full-concrete axes should yield confidence >= 0.5. Got {record.confidence:.2f}"
        )


class TestMemoryStoreUnification:
    """Tests for experience_memory using MemoryStore.append() exclusively.

    M-01 and M-02 use an isolated tmp store (via monkeypatch) so they do NOT
    write to the real memory/data/memory_store.json.  Runtime-generated test
    state must never be committed as code artifacts.
    """

    def test_M01_write_goes_through_memory_store(self, tmp_path, monkeypatch):
        """M-01: write_experience_to_store() uses MemoryStore.append().
        Verifies no direct JSON write: entry is readable back via MemoryStore.all().
        Uses an isolated tmp store to avoid polluting the real MemoryStore.
        """
        import memory.experience_memory as exp_mem
        from memory.experience_memory import create_experience_entry, write_experience_to_store
        from memory.memory_store import MemoryStore

        tmp_store_path = tmp_path / "memory_store.json"

        # Patch MemoryStore inside experience_memory to use the tmp store
        class _IsolatedMemoryStore(MemoryStore):
            def __init__(self):
                super().__init__(store_path=tmp_store_path)

        monkeypatch.setattr(exp_mem, "MemoryStore", _IsolatedMemoryStore)

        entry = create_experience_entry(
            action_id="test-action-M01",
            assessment_id="ASSESS-test-001",
            consequence_id="CONSQ-test-001",
            outcome="SUCCESS",
            execution_success=True,
            consequence_verified=True,
            deviation=[],
            axes_snapshot={"X": "evidence", "Y": "interp", "Z": "auth",
                           "T": "fresh", "S": "ok", "K": "struct"},
        )

        result = write_experience_to_store(entry)
        assert result == True, "write_experience_to_store must return True on success"

        store = MemoryStore(store_path=tmp_store_path)
        experience_entries = [e for e in store.all() if e.memory_type == "experience"]
        matching = [e for e in experience_entries if e.memory_id == entry.memory_id]
        assert len(matching) >= 1, (
            f"Entry {entry.memory_id} must be readable back via MemoryStore.all(). "
            f"Found experience entries: {[e.memory_id for e in experience_entries]}"
        )

    def test_M02_retention_and_memory_id_applied(self, tmp_path, monkeypatch):
        """M-02: MemoryStore applies retention policy; memory_id is present and non-empty.
        Verifies MemoryStore contract is honored for experience entries.
        Uses an isolated tmp store to avoid polluting the real MemoryStore.
        """
        import memory.experience_memory as exp_mem
        from memory.experience_memory import create_experience_entry, write_experience_to_store
        from memory.memory_store import MemoryStore

        tmp_store_path = tmp_path / "memory_store.json"

        class _IsolatedMemoryStore(MemoryStore):
            def __init__(self):
                super().__init__(store_path=tmp_store_path)

        monkeypatch.setattr(exp_mem, "MemoryStore", _IsolatedMemoryStore)

        entry = create_experience_entry(
            action_id="test-action-M02",
            assessment_id="ASSESS-test-002",
            consequence_id="CONSQ-test-002",
            outcome="FAILURE",
            execution_success=False,
            consequence_verified=False,
            deviation=["unexpected_file"],
            axes_snapshot={"X": "UNKNOWN", "Y": "UNKNOWN", "Z": "auth",
                           "T": "fresh", "S": "high", "K": "struct"},
            error_detail="target unreachable",
        )

        write_experience_to_store(entry)

        store = MemoryStore(store_path=tmp_store_path)
        all_entries = store.all()

        experience_entries = [e for e in all_entries if e.memory_type == "experience"]
        assert len(experience_entries) >= 1, "At least one experience entry must exist after write"

        for e in experience_entries:
            assert e.memory_id, "memory_id must be non-empty"
            assert e.memory_type == "experience", f"memory_type must be 'experience', got {e.memory_type}"
            assert e.content, "content must not be empty"
            assert e.timestamp, "timestamp must be non-empty"
