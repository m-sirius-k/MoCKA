# phi_os/runtime/institution_runtime.py
# PHI-OS Institution Runtime v1 — 制度実行基盤 統合入口
# 参照: PHI_OS_CONSTITUTION_v1.md / INSTITUTION_PROTOCOL_v1.md / GATE_ARCHITECTURE_v1.md
#
# すべてのGateはこのRuntimeを経由して制度判定を行う。
# 制度ルールを各Gateへ重複実装してはならない (Phase 5 実装原則 2)。
from typing import Optional

from .runtime_types import (
    Artifact, Meaning, Institution, Authority, Gate,
    BindingResult, ComplianceResult, EventContext,
    MeaningClass, AuthorityType, GateId, BindingStatus,
)
from .runtime_errors import (
    MeaningNotFoundError, InstitutionResolutionError, GateValidationError,
    BindingError, ComplianceViolationError,
)
from .meaning_registry import MeaningRegistry
from .authority_manager import AuthorityManager
from .institution_registry import InstitutionRegistry
from .gate_registry import GateRegistry
from .binding_engine import BindingEngine
from .compliance_engine import ComplianceEngine


class InstitutionRuntime:
    """
    PHI-OS Institution Runtime v1。

    MoCKAの全Gate共通制度実行エンジン。
    Meaning・Institution・Authority・Gate・Bindingを一元管理する。

    使用例:
        runtime = InstitutionRuntime()
        meaning = runtime.resolve_meaning("SYSTEM_CORE")
        result  = runtime.validate_binding(artifact)
        ok, _   = runtime.validate_gate(GateId.EVENT, artifact)
    """

    _instance: Optional["InstitutionRuntime"] = None

    def __init__(self) -> None:
        self.meanings    = MeaningRegistry()
        self.authorities = AuthorityManager()
        self.institutions = InstitutionRegistry()
        self.gates       = GateRegistry()
        self.binding     = BindingEngine(self.meanings, self.institutions, self.gates)
        self.compliance  = ComplianceEngine(
            self.meanings, self.institutions, self.gates,
            self.binding, self.authorities,
        )

    @classmethod
    def get_instance(cls) -> "InstitutionRuntime":
        """シングルトンインスタンスを返す (Runtime共有用)。"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """テスト用リセット。"""
        cls._instance = None

    # ════════════════════════════════════════════════════════════════════════
    # Meaning API
    # ════════════════════════════════════════════════════════════════════════

    def resolve_meaning(self, meaning_id: str) -> Meaning:
        """
        Meaning IDからMeaningを解決する。
        Constitution 原則6: Meaningが制度上の意味を決定する。
        """
        return self.meanings.get(meaning_id)

    def register_meaning(self, meaning: Meaning) -> None:
        self.meanings.register(meaning)

    # ════════════════════════════════════════════════════════════════════════
    # Institution API
    # ════════════════════════════════════════════════════════════════════════

    def resolve_institution(self, institution_id: str) -> Institution:
        """
        Institution IDからInstitutionを解決する。
        Constitution 原則7: すべてのArtifactは単一の主Institutionに帰属する。
        """
        return self.institutions.get(institution_id)

    def register_institution(self, institution: Institution) -> None:
        self.institutions.register(institution)

    # ════════════════════════════════════════════════════════════════════════
    # Authority API
    # ════════════════════════════════════════════════════════════════════════

    def resolve_authority(self, authority_type: AuthorityType) -> Authority:
        """
        AuthorityTypeからAuthorityを解決する。
        Constitution 3.1: Authority体系の正規参照。
        """
        return self.authorities.get(authority_type)

    def resolve_authority_for_gate(self, gate_id: GateId) -> Authority:
        """Gate IDに対応するAuthorityを返す (GATE_ARCHITECTURE_v1.md 4.1)。"""
        return self.authorities.get_for_gate(gate_id)

    # ════════════════════════════════════════════════════════════════════════
    # Binding API
    # ════════════════════════════════════════════════════════════════════════

    def validate_binding(self, artifact: Artifact) -> BindingResult:
        """
        ArtifactのBinding状態を検証する。
        Constitution 4.1: Artifact→Meaning→Institution→Gate の経路を検証。
        """
        return self.binding.validate_binding(artifact)

    def register_artifact(self, artifact: Artifact) -> BindingResult:
        """
        Artifactを制度登録する。
        CONNECTED判定時は Institution.artifact_ids に自動追加する。
        """
        return self.binding.register_binding(artifact)

    # ════════════════════════════════════════════════════════════════════════
    # Gate API
    # ════════════════════════════════════════════════════════════════════════

    def validate_gate(
        self, gate_id: GateId, artifact: Artifact
    ) -> tuple[bool, list[str]]:
        """
        ArtifactがGateを通過できるかを検証する。
        各GateはこのAPIを通じて制度判定を委譲する (実装原則 2)。
        """
        issues: list[str] = []

        # Gate存在確認
        gate = self.gates.get(gate_id)

        # Meaning検証
        meaning_ok, meaning_issues = self.meanings.validate(artifact.meaning_id)
        issues.extend(meaning_issues)

        if meaning_ok:
            meaning = self.meanings.get(artifact.meaning_id)
            gate_ok, gate_issues = self.gates.validate_meaning_for_gate(
                gate_id, meaning.meaning_class
            )
            issues.extend(gate_issues)

        # Institution検証
        if not self.institutions.exists(artifact.institution_id):
            issues.append(f"Institution '{artifact.institution_id}' 未登録 — Gate通過不可")

        return len(issues) == 0, issues

    # ════════════════════════════════════════════════════════════════════════
    # Event Context API
    # ════════════════════════════════════════════════════════════════════════

    def create_event_context(self, artifact: Artifact) -> EventContext:
        """
        Artifactのイベント生成コンテキストを作成する。
        Event Gate は このコンテキストを参照して Event Authority を確認する。
        """
        import uuid
        gate_id = artifact.gate_id or GateId.EVENT
        gate_ok, gate_issues = self.validate_gate(gate_id, artifact)
        authority = self.resolve_authority_for_gate(gate_id)
        binding = self.validate_binding(artifact)

        return EventContext(
            context_id=f"CTX-{uuid.uuid4().hex[:8].upper()}",
            artifact_id=artifact.artifact_id,
            institution_id=artifact.institution_id,
            gate_id=gate_id,
            binding_status=binding.binding_status,
            authority_type=authority.authority_type,
            is_gate_valid=gate_ok,
            issues=gate_issues + binding.issues,
        )

    # ════════════════════════════════════════════════════════════════════════
    # Compliance API
    # ════════════════════════════════════════════════════════════════════════

    def audit(self, artifacts: list[Artifact]) -> ComplianceResult:
        """
        全Artifactの制度監査を実行する。
        Constitution 6.3: Verification Authorityがいつでも実行できる。
        """
        return self.compliance.audit(artifacts)

    def check_compliance(self, artifact: Artifact) -> ComplianceResult:
        """単一Artifactの即時制度チェックを実行する。"""
        return self.compliance.audit([artifact])

    # ════════════════════════════════════════════════════════════════════════
    # Status API
    # ════════════════════════════════════════════════════════════════════════

    def status(self) -> dict:
        """Runtimeの現在状態サマリを返す。"""
        return {
            "runtime": "PHI-OS Institution Runtime v1",
            "meanings": len(self.meanings.all_meanings()),
            "institutions": len(self.institutions.all_institutions()),
            "gates": {
                "total": len(self.gates.all_gates()),
                "active": len(self.gates.active_gates()),
            },
            "authorities": len(self.authorities.all_authorities()),
            "bindings": len(self.binding.get_all_bindings()),
            "authority_conflicts": len(self.authorities.detect_conflicts()),
        }
