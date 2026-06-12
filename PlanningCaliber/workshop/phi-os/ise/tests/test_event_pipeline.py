# test_event_pipeline.py
"""STEP 2: EventPipeline 検証"""
import pytest

from .. import decision_ledger
from ..state_builder import emit_event
from phios.core.event_pipeline import EventPipeline, pipeline


@pytest.fixture
def isolated_ledger(tmp_path, monkeypatch):
    monkeypatch.setattr(decision_ledger, "LEDGER_PATH", tmp_path / "decision_ledger.jsonl")


def test_pipeline_valid_event_ok(isolated_ledger):
    result = pipeline.emit("STATE_INIT", actor="Claude")
    assert result["event_type"] == "STATE_INIT"
    assert result["category"] == "state_transition"


def test_pipeline_invalid_event_raises(isolated_ledger):
    with pytest.raises(ValueError):
        pipeline.emit("NOT_A_REAL_EVENT")


def test_pipeline_single_path_only(isolated_ledger):
    # state_builder.emit_event はEventPipeline.emit経由の単一経路
    result = emit_event("STATE_INIT", actor="Claude")
    assert result["event_type"] == "STATE_INIT"
    assert isinstance(pipeline, EventPipeline)


def test_pipeline_revision_increment(isolated_ledger):
    result = pipeline.emit("STATE_DEGRADED", actor="ISE", before="active", after="degraded", reason="timeout")
    assert result["revision_increment"] is True


def test_pipeline_no_revision_on_seal(isolated_ledger):
    result = pipeline.emit("SEAL", actor="mocka-seal")
    assert result["revision_increment"] is False


def test_pipeline_critical_audit_hook(isolated_ledger, monkeypatch):
    called = []
    monkeypatch.setattr(EventPipeline, "_audit_hook", lambda self, entry: called.append(entry))

    result = pipeline.emit(
        "AUTHORITY_REVOKE", actor="Human", before="delegated", after="revoked", reason="test"
    )
    assert result["severity"] == "critical"
    assert len(called) == 1
    assert called[0]["event_type"] == "AUTHORITY_REVOKE"


def test_pipeline_audit_hook_failure_does_not_block(isolated_ledger, monkeypatch):
    def boom(self, entry):
        raise RuntimeError("audit hook failure")

    monkeypatch.setattr(EventPipeline, "_audit_hook", boom)

    # _audit_hookが例外を出してもemit()全体は成功する
    result = pipeline.emit(
        "AUTHORITY_REVOKE", actor="Human", before="delegated", after="revoked", reason="test"
    )
    assert result["event_type"] == "AUTHORITY_REVOKE"
