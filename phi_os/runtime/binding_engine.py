# phi_os/runtime/binding_engine.py
# Institution Runtime — Binding Layer実行エンジン
# 参照: PHI_OS_CONSTITUTION_v1.md 第4章 Binding原則
from typing import Optional

from .runtime_types import (
    Artifact, BindingResult, BindingStatus, MeaningClass, GateId,
)
from .runtime_errors import (
    BindingError, OrphanArtifactError, ShadowArtifactError, DuplicateBindingError,
)
from .meaning_registry import MeaningRegistry
from .institution_registry import InstitutionRegistry
from .gate_registry import GateRegistry


class BindingEngine:
    """
    Artifact → Meaning → Institution → Gate の制度接続を実行する。
    Constitution 4.1: 制度接続の唯一正規経路を検証・解決する。
    """

    def __init__(
        self,
        meaning_registry: MeaningRegistry,
        institution_registry: InstitutionRegistry,
        gate_registry: GateRegistry,
    ) -> None:
        self._meanings = meaning_registry
        self._institutions = institution_registry
        self._gates = gate_registry
        self._binding_store: dict[str, BindingResult] = {}

    # ── 主要API ──────────────────────────────────────────────────────────────

    def validate_binding(self, artifact: Artifact) -> BindingResult:
        """
        ArtifactのBinding状態を検証する。
        Constitution 4.1 の正規経路: Artifact→Meaning→Institution→Gate を順検証。
        """
        issues: list[str] = []

        # Step 1: Meaning検証
        meaning_ok, meaning_issues = self._meanings.validate(artifact.meaning_id)
        issues.extend(meaning_issues)

        # Step 2: Institution検証
        if not self._institutions.exists(artifact.institution_id):
            issues.append(f"Institution '{artifact.institution_id}' 未登録 — ORPHAN候補")

        # Step 3: Gate検証
        gate_id = artifact.gate_id
        if gate_id is None:
            issues.append("Gate未割当")
        else:
            gate = self._gates.get(gate_id)
            if artifact.meaning_id and meaning_ok:
                meaning = self._meanings.get(artifact.meaning_id)
                gate_ok, gate_issues = self._gates.validate_meaning_for_gate(
                    gate_id, meaning.meaning_class
                )
                issues.extend(gate_issues)

        # Step 4: 総合判定
        binding_status = _determine_status(artifact, issues)
        result = BindingResult(
            artifact_id=artifact.artifact_id,
            binding_status=binding_status,
            meaning_id=artifact.meaning_id if meaning_ok else None,
            institution_id=artifact.institution_id if self._institutions.exists(artifact.institution_id) else None,
            gate_id=gate_id,
            is_valid=(binding_status == BindingStatus.CONNECTED),
            issues=issues,
        )
        self._binding_store[artifact.artifact_id] = result
        return result

    def resolve_binding(self, artifact_id: str) -> BindingResult:
        """登録済みBindingResultを返す。未登録の場合はBindingError。"""
        if artifact_id not in self._binding_store:
            raise BindingError(artifact_id, "Binding未評価。validate_binding()を先に実行すること")
        return self._binding_store[artifact_id]

    def register_binding(self, artifact: Artifact) -> BindingResult:
        """Artifactを制度登録し、Binding結果をストアに保存する。"""
        # 重複CONNECTED登録チェック
        if artifact.artifact_id in self._binding_store:
            existing = self._binding_store[artifact.artifact_id]
            if existing.binding_status == BindingStatus.CONNECTED:
                raise DuplicateBindingError(artifact.artifact_id)

        result = self.validate_binding(artifact)
        if result.is_valid:
            self._institutions.register_artifact(artifact.artifact_id, artifact.institution_id)
        return result

    # ── 異常検知 ─────────────────────────────────────────────────────────────

    def detect_orphan(self, artifact: Artifact) -> bool:
        """Institution未帰属のArtifactを検出する (Constitution 原則7)。"""
        return not self._institutions.exists(artifact.institution_id)

    def detect_shadow(self, artifact: Artifact) -> bool:
        """
        Gate外部に存在するArtifactを検出する。
        Meaningが定義されているがGate通過記録がない場合をSHADOWとする。
        """
        if artifact.gate_id is None:
            return True
        if not self._meanings.exists(artifact.meaning_id):
            return False  # UNKNOWNであってSHADOWではない
        return artifact.binding_status == BindingStatus.SHADOW

    def detect_duplicate_binding(self, artifact_id: str) -> bool:
        """同一ArtifactのCONNECTED重複登録を検出する。"""
        existing = self._binding_store.get(artifact_id)
        if existing and existing.binding_status == BindingStatus.CONNECTED:
            return True
        return False

    # ── バルク検査 ───────────────────────────────────────────────────────────

    def scan_all(self, artifacts: list[Artifact]) -> dict[str, BindingResult]:
        """全Artifactのバインディングを一括検査する。"""
        results: dict[str, BindingResult] = {}
        for a in artifacts:
            results[a.artifact_id] = self.validate_binding(a)
        return results

    def get_all_bindings(self) -> dict[str, BindingResult]:
        return dict(self._binding_store)


# ── 内部ヘルパー ─────────────────────────────────────────────────────────────

def _determine_status(artifact: Artifact, issues: list[str]) -> BindingStatus:
    """検証結果からBinding状態を決定する。"""
    if not issues:
        return BindingStatus.CONNECTED

    # Orphan判定: Institutionなし
    if any("ORPHAN" in i for i in issues):
        return BindingStatus.ORPHAN

    # Unknown判定: Meaning未定義
    if any("未登録" in i and "Meaning" in i for i in issues):
        return BindingStatus.UNKNOWN

    # Shadow判定: 既存がSHADOW
    if artifact.binding_status == BindingStatus.SHADOW:
        return BindingStatus.SHADOW

    # Deprecated判定
    if artifact.binding_status == BindingStatus.DEPRECATED:
        return BindingStatus.DEPRECATED

    # 上記以外は接続不完全
    return BindingStatus.PARTIAL
