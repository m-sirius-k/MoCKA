# phi_os/tests/test_institution_runtime.py
# Institution Runtime 単体テスト
# 制度判定・異常系を含む
import pytest

from phi_os.runtime import (
    InstitutionRuntime,
    Artifact, Meaning, Institution,
    BindingStatus, MeaningClass, AuthorityType, GateId, ViolationSeverity,
    MeaningNotFoundError, GateValidationError, InstitutionResolutionError,
    OrphanArtifactError, DuplicateBindingError, AuthorityConflictError,
)


@pytest.fixture(autouse=True)
def reset_runtime():
    InstitutionRuntime.reset()
    yield
    InstitutionRuntime.reset()


@pytest.fixture
def rt() -> InstitutionRuntime:
    return InstitutionRuntime()


def _artifact(
    aid: str = "ART-001",
    meaning_id: str = "SYSTEM_CORE",
    institution_id: str = "PHI-OS",
    gate_id: GateId = GateId.EVENT,
    binding_status: BindingStatus = BindingStatus.UNKNOWN,
) -> Artifact:
    return Artifact(
        artifact_id=aid,
        name=aid,
        path=f"/phi_os/{aid}.py",
        meaning_id=meaning_id,
        institution_id=institution_id,
        gate_id=gate_id,
        binding_status=binding_status,
    )


# ════════════════════════════════════════════════════════════════════════════
# MeaningRegistry
# ════════════════════════════════════════════════════════════════════════════

class TestMeaningRegistry:
    def test_resolve_default_meaning(self, rt):
        m = rt.resolve_meaning("SYSTEM_CORE")
        assert m.meaning_class == MeaningClass.SYSTEM_CORE

    def test_resolve_unknown_raises(self, rt):
        with pytest.raises(MeaningNotFoundError):
            rt.resolve_meaning("DOES_NOT_EXIST")

    def test_register_custom_meaning(self, rt):
        m = Meaning("CUSTOM", "Custom", MeaningClass.DESIGN, "テスト用")
        rt.register_meaning(m)
        assert rt.resolve_meaning("CUSTOM").meaning_class == MeaningClass.DESIGN

    def test_unclassified_meaning_fails_validation(self, rt):
        ok, issues = rt.meanings.validate("UNCLASSIFIED")
        assert not ok
        assert any("UNCLASSIFIED" in i for i in issues)

    def test_change_history_recorded(self, rt):
        rt.meanings.update_class("TOOL", MeaningClass.GOVERNANCE, "テスト変更")
        history = rt.meanings.change_history("TOOL")
        assert len(history) == 1
        assert history[0]["reason"] == "テスト変更"


# ════════════════════════════════════════════════════════════════════════════
# AuthorityManager
# ════════════════════════════════════════════════════════════════════════════

class TestAuthorityManager:
    def test_resolve_gate_authority(self, rt):
        auth = rt.resolve_authority(AuthorityType.GATE)
        assert auth.holder == "PHI-OS"

    def test_authority_for_event_gate(self, rt):
        auth = rt.resolve_authority_for_gate(GateId.EVENT)
        assert auth.authority_type == AuthorityType.EVENT

    def test_no_conflict_by_default(self, rt):
        conflicts = rt.authorities.detect_conflicts()
        assert conflicts == []

    def test_gate_authority_cannot_delegate(self, rt):
        with pytest.raises(AuthorityConflictError):
            rt.authorities.delegate(AuthorityType.GATE, "SomeOther", "EVT-001")

    def test_event_authority_cannot_delegate(self, rt):
        with pytest.raises(AuthorityConflictError):
            rt.authorities.delegate(AuthorityType.EVENT, "SomeOther", "EVT-001")

    def test_gate_authority_can_override_subordinates(self, rt):
        assert rt.authorities.can_override(AuthorityType.GATE, AuthorityType.EVENT)
        assert rt.authorities.can_override(AuthorityType.GATE, AuthorityType.KNOWLEDGE)

    def test_event_authority_cannot_override_gate(self, rt):
        assert not rt.authorities.can_override(AuthorityType.EVENT, AuthorityType.GATE)


# ════════════════════════════════════════════════════════════════════════════
# InstitutionRegistry
# ════════════════════════════════════════════════════════════════════════════

class TestInstitutionRegistry:
    def test_resolve_default_institution(self, rt):
        inst = rt.resolve_institution("PHI-OS")
        assert inst.institution_id == "PHI-OS"

    def test_resolve_unknown_raises(self, rt):
        with pytest.raises(InstitutionResolutionError):
            rt.resolve_institution("DOES_NOT_EXIST")

    def test_register_artifact_to_institution(self, rt):
        rt.institutions.register_artifact("ART-999", "MoCKA")
        assert rt.institutions.is_member("ART-999", "MoCKA")

    def test_find_institution_of(self, rt):
        rt.institutions.register_artifact("ART-555", "Orchestra")
        result = rt.institutions.find_institution_of("ART-555")
        assert result == "Orchestra"

    def test_get_scope(self, rt):
        scope = rt.institutions.get_scope("PHI-OS")
        assert scope["primary_gate"] == GateId.EVENT.value


# ════════════════════════════════════════════════════════════════════════════
# GateRegistry
# ════════════════════════════════════════════════════════════════════════════

class TestGateRegistry:
    def test_all_7_gates_registered(self, rt):
        assert len(rt.gates.all_gates()) == 7

    def test_event_gate_active(self, rt):
        from phi_os.runtime.runtime_types import GateStatus
        g = rt.gates.get(GateId.EVENT)
        assert g.status == GateStatus.ACTIVE

    def test_valid_transition(self, rt):
        ok, issues = rt.gates.validate_transition(GateId.DOCUMENT, GateId.EVENT)
        assert ok

    def test_invalid_transition(self, rt):
        ok, issues = rt.gates.validate_transition(GateId.EVENT, GateId.MODULE)
        assert not ok

    def test_knowledge_gate_requires_knowledge_meaning(self, rt):
        ok, _ = rt.gates.validate_meaning_for_gate(GateId.KNOWLEDGE, MeaningClass.KNOWLEDGE)
        assert ok

    def test_knowledge_gate_rejects_system_core(self, rt):
        ok, issues = rt.gates.validate_meaning_for_gate(GateId.KNOWLEDGE, MeaningClass.SYSTEM_CORE)
        assert not ok

    def test_get_capabilities(self, rt):
        caps = rt.gates.get_capabilities(GateId.EVENT)
        assert caps["gate_id"] == "GATE-EVENT"
        assert "authority" in caps


# ════════════════════════════════════════════════════════════════════════════
# BindingEngine
# ════════════════════════════════════════════════════════════════════════════

class TestBindingEngine:
    def test_valid_artifact_is_connected(self, rt):
        art = _artifact()
        result = rt.validate_binding(art)
        assert result.binding_status == BindingStatus.CONNECTED
        assert result.is_valid

    def test_unknown_meaning_gives_unknown_status(self, rt):
        art = _artifact(meaning_id="NO_SUCH_MEANING")
        result = rt.validate_binding(art)
        assert result.binding_status == BindingStatus.UNKNOWN
        assert not result.is_valid

    def test_unknown_institution_gives_orphan(self, rt):
        art = _artifact(institution_id="PHANTOM_INST")
        result = rt.validate_binding(art)
        assert result.binding_status == BindingStatus.ORPHAN

    def test_no_gate_gives_partial(self, rt):
        art = _artifact(gate_id=None)
        art.gate_id = None
        result = rt.validate_binding(art)
        assert result.binding_status in (BindingStatus.PARTIAL, BindingStatus.UNKNOWN)

    def test_register_artifact_connected(self, rt):
        art = _artifact(aid="REG-001")
        result = rt.register_artifact(art)
        assert result.is_valid
        assert rt.institutions.is_member("REG-001", "PHI-OS")

    def test_duplicate_connected_raises(self, rt):
        art = _artifact(aid="DUP-001")
        rt.register_artifact(art)
        with pytest.raises(DuplicateBindingError):
            rt.register_artifact(art)

    def test_detect_orphan(self, rt):
        art = _artifact(institution_id="GHOST")
        assert rt.binding.detect_orphan(art)

    def test_detect_shadow(self, rt):
        art = _artifact(binding_status=BindingStatus.SHADOW)
        art.gate_id = None
        assert rt.binding.detect_shadow(art)


# ════════════════════════════════════════════════════════════════════════════
# ComplianceEngine
# ════════════════════════════════════════════════════════════════════════════

class TestComplianceEngine:
    def test_valid_artifact_no_violations(self, rt):
        art = _artifact()
        rt.validate_binding(art)
        result = rt.audit([art])
        assert result.is_compliant
        assert result.violations == []

    def test_gate_bypass_detected(self, rt):
        art = _artifact(gate_id=None)
        art.gate_id = None
        violations = rt.compliance.check_gate_bypass(art)
        assert len(violations) == 1
        assert violations[0].severity == ViolationSeverity.CRITICAL
        assert violations[0].violation_type == "GATE_BYPASS"

    def test_undefined_meaning_detected(self, rt):
        art = _artifact(meaning_id="UNDEFINED_XXX")
        violations = rt.compliance.check_undefined_meaning(art)
        assert any(v.violation_type == "MEANING_UNDEFINED" for v in violations)

    def test_institution_missing_detected(self, rt):
        art = _artifact(institution_id="MISSING_INST")
        violations = rt.compliance.check_institution_missing(art)
        assert any(v.violation_type == "INSTITUTION_MISSING" for v in violations)

    def test_orphan_artifact_audit_violation(self, rt):
        art = _artifact(institution_id="PHANTOM")
        rt.validate_binding(art)
        result = rt.audit([art])
        assert not result.is_compliant
        assert any(v.violation_type == "INSTITUTION_MISSING" for v in result.violations)

    def test_invalid_event_id_detected(self, rt):
        violations = rt.compliance.check_event_invalid_generation({"event_id": "MANUAL-001"})
        assert violations[0].violation_type == "EVENT_INVALID_ID"

    def test_valid_event_id_accepted(self, rt):
        violations = rt.compliance.check_event_invalid_generation({"event_id": "E20260616_001"})
        assert violations == []


# ════════════════════════════════════════════════════════════════════════════
# InstitutionRuntime 統合
# ════════════════════════════════════════════════════════════════════════════

class TestInstitutionRuntime:
    def test_singleton_pattern(self):
        a = InstitutionRuntime.get_instance()
        b = InstitutionRuntime.get_instance()
        assert a is b

    def test_status_summary(self, rt):
        s = rt.status()
        assert s["meanings"] >= 9
        assert s["institutions"] >= 8
        assert s["gates"]["total"] == 7
        assert s["gates"]["active"] >= 6

    def test_create_event_context(self, rt):
        art = _artifact()
        ctx = rt.create_event_context(art)
        assert ctx.is_gate_valid
        assert ctx.gate_id == GateId.EVENT
        assert ctx.authority_type == AuthorityType.EVENT

    def test_validate_gate_for_event_gate(self, rt):
        art = _artifact()
        ok, issues = rt.validate_gate(GateId.EVENT, art)
        assert ok
        assert issues == []

    def test_validate_gate_wrong_meaning_for_knowledge_gate(self, rt):
        art = _artifact(gate_id=GateId.KNOWLEDGE)
        ok, issues = rt.validate_gate(GateId.KNOWLEDGE, art)
        # SYSTEM_CORE は Knowledge Gate を通過できない
        assert not ok

    def test_full_pipeline_connected(self, rt):
        """Artifact→Meaning→Institution→Gate の全経路が制度接続されることを確認"""
        art = Artifact(
            artifact_id="PIPE-001",
            name="pipeline_test",
            path="/phi_os/runtime/institution_runtime.py",
            meaning_id="SYSTEM_CORE",
            institution_id="PHI-OS",
            gate_id=GateId.MODULE,
        )
        result = rt.register_artifact(art)
        assert result.is_valid
        assert result.binding_status == BindingStatus.CONNECTED
        ctx = rt.create_event_context(art)
        assert ctx.binding_status == BindingStatus.CONNECTED
        audit = rt.audit([art])
        assert audit.is_compliant
