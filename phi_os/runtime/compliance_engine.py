# phi_os/runtime/compliance_engine.py
# Institution Runtime — 制度監査エンジン
# 参照: PHI_OS_CONSTITUTION_v1.md 第5〜6章 / GATE_ARCHITECTURE_v1.md 第5章
import uuid
from datetime import datetime, timezone

from .runtime_types import (
    Artifact, ComplianceResult, ComplianceViolation,
    ViolationSeverity, BindingStatus, GateId, MeaningClass,
)
from .meaning_registry import MeaningRegistry
from .institution_registry import InstitutionRegistry
from .gate_registry import GateRegistry
from .binding_engine import BindingEngine
from .authority_manager import AuthorityManager


class ComplianceEngine:
    """
    制度違反の検知エンジン。
    Constitution 6.2: 違反分類 Critical/High/Medium/Low を返す。
    各Gateは制度判定をここに委譲する（重複実装禁止）。
    """

    def __init__(
        self,
        meaning_registry: MeaningRegistry,
        institution_registry: InstitutionRegistry,
        gate_registry: GateRegistry,
        binding_engine: BindingEngine,
        authority_manager: AuthorityManager,
    ) -> None:
        self._meanings = meaning_registry
        self._institutions = institution_registry
        self._gates = gate_registry
        self._binding = binding_engine
        self._authority = authority_manager

    # ── 全件監査 ─────────────────────────────────────────────────────────────

    def audit(self, artifacts: list[Artifact]) -> ComplianceResult:
        """
        全Artifactの制度監査を実行する。
        Constitution 6.3: Verification Authorityはいつでも実行できる。
        """
        audit_id = f"AUDIT-{uuid.uuid4().hex[:8].upper()}"
        violations: list[ComplianceViolation] = []

        for artifact in artifacts:
            violations.extend(self._check_artifact(artifact))

        # Authority競合チェック
        conflicts = self._authority.detect_conflicts()
        for conflict in conflicts:
            violations.append(ComplianceViolation(
                violation_id=_vid(),
                severity=ViolationSeverity.CRITICAL,
                violation_type="AUTHORITY_CONFLICT",
                target_artifact_id=None,
                description=f"Authority重複: {conflict['holder']} が {conflict['authority_types']} を保持",
                remediation="Gate Authorityが最終裁定を行い、Authority割当を修正すること (Constitution 3.2)",
            ))

        is_compliant = len(violations) == 0
        summary = (
            f"監査完了: {len(artifacts)}件中違反{len(violations)}件"
            + (" — ALL COMPLIANT" if is_compliant else " — 違反あり、修復が必要")
        )
        return ComplianceResult(
            audit_id=audit_id,
            is_compliant=is_compliant,
            violations=violations,
            audited_artifacts=len(artifacts),
            summary=summary,
        )

    # ── 個別チェック ──────────────────────────────────────────────────────────

    def check_gate_bypass(self, artifact: Artifact) -> list[ComplianceViolation]:
        """Gate迂回検知 (Constitution 5.3 / GATE_ARCHITECTURE_v1.md 5.1 Critical)"""
        violations: list[ComplianceViolation] = []
        if artifact.gate_id is None:
            violations.append(ComplianceViolation(
                violation_id=_vid(),
                severity=ViolationSeverity.CRITICAL,
                violation_type="GATE_BYPASS",
                target_artifact_id=artifact.artifact_id,
                description=f"Artifact '{artifact.artifact_id}' にGate未割当 — Gate迂回の疑い",
                remediation="適切なGateを経由してArtifactを再登録すること",
            ))
        return violations

    def check_authority_duplication(self) -> list[ComplianceViolation]:
        """Authority重複検知 (Constitution 5.5 Critical)"""
        violations: list[ComplianceViolation] = []
        conflicts = self._authority.detect_conflicts()
        for c in conflicts:
            violations.append(ComplianceViolation(
                violation_id=_vid(),
                severity=ViolationSeverity.CRITICAL,
                violation_type="AUTHORITY_DUPLICATION",
                target_artifact_id=None,
                description=f"Authority一意性違反: {c}",
                remediation="Authority割当を修正し、重複を解消すること",
            ))
        return violations

    def check_undefined_meaning(self, artifact: Artifact) -> list[ComplianceViolation]:
        """Meaning未定義検知 (Constitution 5.2 / 原則6)"""
        violations: list[ComplianceViolation] = []
        if not self._meanings.exists(artifact.meaning_id):
            violations.append(ComplianceViolation(
                violation_id=_vid(),
                severity=ViolationSeverity.HIGH,
                violation_type="MEANING_UNDEFINED",
                target_artifact_id=artifact.artifact_id,
                description=f"Meaning '{artifact.meaning_id}' 未定義 — UNCLASSIFIED状態",
                remediation="Meaning Authorityを参照してMeaningを定義・登録すること",
            ))
        return violations

    def check_binding_disconnected(self, artifact: Artifact) -> list[ComplianceViolation]:
        """Binding切断検知 (Constitution 4.2)"""
        violations: list[ComplianceViolation] = []
        binding = self._binding.get_all_bindings().get(artifact.artifact_id)
        if binding is None:
            return violations
        if binding.binding_status in (BindingStatus.ORPHAN, BindingStatus.UNKNOWN):
            violations.append(ComplianceViolation(
                violation_id=_vid(),
                severity=ViolationSeverity.HIGH,
                violation_type="BINDING_DISCONNECTED",
                target_artifact_id=artifact.artifact_id,
                description=f"Binding切断: status={binding.binding_status.value} issues={binding.issues}",
                remediation="制度接続経路 (Artifact→Meaning→Institution→Gate) を修復すること",
            ))
        return violations

    def check_institution_missing(self, artifact: Artifact) -> list[ComplianceViolation]:
        """Institution未所属検知 (Constitution 原則7 / 5.2)"""
        violations: list[ComplianceViolation] = []
        if not self._institutions.exists(artifact.institution_id):
            violations.append(ComplianceViolation(
                violation_id=_vid(),
                severity=ViolationSeverity.HIGH,
                violation_type="INSTITUTION_MISSING",
                target_artifact_id=artifact.artifact_id,
                description=f"Institution '{artifact.institution_id}' 未登録 — ORPHAN状態",
                remediation="Institutionを登録するか、Artifactを既存Institutionに帰属させること",
            ))
        return violations

    def check_event_invalid_generation(self, payload: dict) -> list[ComplianceViolation]:
        """
        Event不正生成検知 (Constitution 5.1)。
        Event ID手動入力・DB直接書き込みの痕跡を検出する。
        """
        violations: list[ComplianceViolation] = []
        event_id = payload.get("event_id", "")
        # 手動IDはEで始まらない、または形式が合わない
        if event_id and not _valid_event_id_format(event_id):
            violations.append(ComplianceViolation(
                violation_id=_vid(),
                severity=ViolationSeverity.CRITICAL,
                violation_type="EVENT_INVALID_ID",
                target_artifact_id=None,
                description=f"Event ID '{event_id}' の形式不正 — 手動入力の疑い",
                remediation="Event IDは自動採番のみ許可 (E{YYYYMMDD}_{NNN}) (Constitution 5.1)",
            ))
        return violations

    # ── 内部ヘルパー ─────────────────────────────────────────────────────────

    def _check_artifact(self, artifact: Artifact) -> list[ComplianceViolation]:
        violations: list[ComplianceViolation] = []
        violations.extend(self.check_gate_bypass(artifact))
        violations.extend(self.check_undefined_meaning(artifact))
        violations.extend(self.check_institution_missing(artifact))
        violations.extend(self.check_binding_disconnected(artifact))
        return violations


# ── ユーティリティ ────────────────────────────────────────────────────────────

def _vid() -> str:
    return f"VIO-{uuid.uuid4().hex[:8].upper()}"


def _valid_event_id_format(event_id: str) -> bool:
    """E{YYYYMMDD}_{NNN} 形式の検証"""
    import re
    return bool(re.match(r'^E\d{8}_\d{3,}$', event_id))
